from fastapi import HTTPException
import phonenumbers
from http.client import HTTPException
import requests



def get_coordinates_for_address(address: str):
    """Convert an address to geographic coordinates, returning bottom-left and top-right coordinates."""
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            # Using viewport for area extents
            location = data['results'][0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
            return {
                "latitude": latitude,
                "longitude": longitude
            }
        else:
            raise HTTPException(status_code=404, detail="Address not found.")
    else:
        raise HTTPException(status_code=response.status_code, detail="Error contacting the geocoding service.")


def validate_phone_number(phone_number: str):
    """
    Validates that a phone number starts with '+' and is a legitimate phone number.
    If only a country code is provided (e.g., '+1'), it is not considered an error.
    """
    if phone_number and len(phone_number) <= 3:  # Assuming country codes are 3 digits max
        return  # Treat as no input and do not raise an exception
    if phone_number and not phone_number.startswith('+'):
        raise HTTPException(
            status_code=400,
            detail="Phone number must start with '+'"
        )
    try:
        parsed_number = phonenumbers.parse(phone_number)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError
    except (phonenumbers.NumberParseException, ValueError):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phone number: {phone_number}"
        )

def get_business_details(place_id: str):
    try:
        # Google Places API Details endpoint URL
        api_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={GOOGLE_MAPS_API_KEY}"

        # Fetch data from Google Places API Details endpoint
        response = requests.get(api_url)
        response.raise_for_status()

        # Parse response JSON
        data = response.json()

        # Extract required fields from the JSON response
        if data['status'] == 'OK':
            result = data['result']
            name = result.get('name', '')
            is_online = 'online' in result.get('types', [])
            address = result.get('formatted_address', '')
            country = next((component['long_name'] for component in result.get('address_components', []) if
                            'country' in component['types']), '')
            state = next((component['long_name'] for component in result.get('address_components', []) if
                          'administrative_area_level_1' in component['types']), '')
            city = next((component['long_name'] for component in result.get('address_components', []) if
                         'locality' in component['types']), '')
            category_list = result.get('types', [])
            description = result.get('editorial_summary', {}).get('overview', '')
            website = result.get('website', '')
            tel_number = result.get('formatted_phone_number', '')
            whatsapp_number = ''  # Assuming there is no direct field for WhatsApp number
            user_rating_count = result.get('user_ratings_total', 0)
            rating = result.get('rating', 0.0)
            photos = [{'photo_reference': photo['photo_reference'], 'height': photo['height'], 'width': photo['width'], 'html_attributions': photo['html_attributions']} for photo in result.get('photos', [])]

            return {
                'name': name,
                'address': address,
                'country': country,
                'state': state,
                'city': city,
                'website': website,
                'tel_number': tel_number,
                'user_rating_count': user_rating_count,
                'rating': rating,
                'place_id': place_id,
                'photos': photos
            }
        else:
            print('Error in API response:', data['status'])
            return None
    except requests.exceptions.RequestException as e:
        print('Error fetching data:', e)
        return None


def get_photo(place_id, max_width=400):
    try:
        # Get business details
        business_details = get_business_details(place_id)
        print("business_details", business_details)

        if business_details and 'photos' in business_details:
            # Get up to 3 photo references
            photo_references = [photo['photo_reference'] for photo in business_details['photos'][:3]]

            photo_urls = []
            print("Photos", photo_references)
            for photo_reference in photo_references:
                # Google Places API Photo endpoint URL
                api_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={GOOGLE_MAPS_API_KEY}"

                # Fetch the photo from Google Places API Photo endpoint
                response = requests.get(api_url, allow_redirects=True)
                response.raise_for_status()

                # The response is a redirect to the actual photo URL
                photo_urls.append(response.url)

            return photo_urls
        else:
            return []
    except requests.exceptions.RequestException as e:
        return []