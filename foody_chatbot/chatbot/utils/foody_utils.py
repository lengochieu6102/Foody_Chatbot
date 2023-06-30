import requests
from typing import Dict, List, Optional, Union

foody_url = "https://www.foody.vn"
from  urllib.parse import quote as url_encode

class FoodySearch:

    def __init__(self):
        self.province_id = 217
        self.foody_url = "https://www.foody.vn"

        self.districts = self.get_district()
        self.cuisines = self.get_cuisine()
        self.categories = self.get_category()

    def get_district(self):
        district_url = f"{self.foody_url}/__get/Directory/GetSearchFilter?t=1686916320422&ds=Restaurant&vt=row&st=1&q=&filter=district&provinceId={self.province_id}"
        district_response = requests.get(district_url, headers = {
                'User-Agent': 'Request-Promise',
                'X-Requested-With': 'XMLHttpRequest'
        })

        district_metadata = district_response.json()
        district_metadata = {district['Name']: str(district['Id']) for district in district_metadata['allDistricts']}
        return district_metadata

    def get_cuisine(self):
        cuisine_url = f"{self.foody_url}/__get/Directory/GetSearchFilter?t=1686916289355&ds=Restaurant&vt=row&st=1&q=&filter=cuisine&provinceId={self.province_id}"

        cuisine_response = requests.get(cuisine_url, headers = {
                'User-Agent': 'Request-Promise',
                'X-Requested-With': 'XMLHttpRequest'
        })
        cuisine_metadata = cuisine_response.json()
        cuisine_metadata = {cuisine['Name']: str(cuisine['Id']) for cuisine in cuisine_metadata['allCuisines']}
        return cuisine_metadata

    def get_category(self):
        category_url = f"{self.foody_url}/__get/Directory/GetSearchFilter?t=1686916724872&ds=Restaurant&vt=row&st=1&q=&filter=category&provinceId={self.province_id}"

        category_response = requests.get(category_url, headers = {
                'User-Agent': 'Request-Promise',
                'X-Requested-With': 'XMLHttpRequest'
        })
        category_metadata = category_response.json()
        category_metadata = {category['Name']: str(category['Id']) for category in category_metadata['allCategories']}
        return category_metadata
    
    def get_district_id(self, district):
        result_id = None
        min_distance = 10e6
        for district_name, district_id in self.districts.items():
            distance = edit_distance(district.lower(), district_name.lower())
            if distance < min_distance:
                min_distance = distance
                result_id = district_id

        return result_id


    def GetRestaurants(
            self,
            cuisines: str,
            districts: str,
            provinceId: Union[int, str, None] = None,
            debug: bool = False
    ):
        if provinceId is None:
            provinceId = self.province_id

        filter_url = f"{self.foody_url}/__get/Directory/GetSearchUrl?page=1&append=false&ds=Restaurant&vt=row&provinceId={provinceId}&st=1"

        if cuisines:
            filter_url += f"&q={url_encode(cuisines)}"
        
        if districts:
            districts = self.get_district_id(districts)
            filter_url += f"&dt={districts}"

        if debug:
            print("districts:", districts)
            print("cuisines:", cuisines)
            print("filter_url:", filter_url)

        filter_response = requests.get(filter_url, headers = {
                'User-Agent': 'Request-Promise',
                'X-Requested-With': 'XMLHttpRequest'
        })

        search_url = filter_response.json()['Url']
        search_url = f"{foody_url}{search_url}"
        
        search_response = requests.get(search_url, headers = {
                'User-Agent': 'Request-Promise',
                'X-Requested-With': 'XMLHttpRequest'
        })
        search_json = search_response.json()
        results_res = "Dưới đây là một số món ăn tôi tìm được: "
        add_info_res = []
        for idx, search_item in enumerate(search_json['searchItems']):
            if results_res:
                results_res += "\n"
            results_res += f"{idx+1}. {search_item['Name']}"
            add_info_res.append({
                'name': search_item['Name'],
                'url': self.foody_url + search_item['DetailUrl'],
                'image_url': search_item['PicturePathLarge'],
                'address': search_item['Address']
            })
        
        return {
            "search_object": search_json,
            "restaurants_response": results_res,
            "add_info_res": add_info_res
        }

def edit_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]