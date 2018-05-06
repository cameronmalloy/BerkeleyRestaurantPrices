import requests
import numpy as np
import pandas as pd

auth = {"Authorization": "Bearer #SECRET..."}
search_lst = ["location=94709", "term=restaurant"]
student_zips = [94704, 94709]
non_student_zips = [94702, 94703, 94705, 94710]
limit = 50

def get_lst_prices(lst):
    """
    Params:
        lst: list of zip codes
    Return:
        A list of restaurants and a list or prices. Each index for each list corresponds with each other
    """
    restaurant_lst = []
    prices_lst = []
    for elm in lst:
        search_lst[0] = "location=" + str(elm)
        prices = get_prices(elm)
        restaurant_lst += list(prices.keys())
        prices_lst += (list(prices.values()))
    return restaurant_lst, prices_lst

def search_req(offset, lst=search_lst, fast_food=False):
    """
    Params:
        offset: number of results to skip
        lst: list of zip codes
        fast_food: whether you want to search for fast food restaurants
    Return:
        Returns a search request of 50 items with the given offset and parameters in the given list
        For our project purposes, I added an optional parameter to search for exclusively fast food restaurants
    """
    str_req = "https://api.yelp.com/v3/businesses/search?"
    for param in lst:
        str_req += param
        str_req += "&"
    if fast_food:
        str_req += "categories=hotdogs&"
    str_req += "limit=" + str(limit)
    str_req += "&offset=" + str(offset)
    print(str_req)
    return requests.get(str_req, headers=auth).json()

def get_prices(zip_code, ff = False, location = False):
    """
    Params:
        zip_code: zip code
        ff: whether you want to return info on fast food resaurants only
        location: whether you want to return lat's and long's of restaurants
    Return:
        a dictionary that maps restaurant names to prices (1 to 4, with the number representing the number of $'s)
        (optional ff) number of fast food restaurants found in query
        (obtional location) 2 dictionaries:
            [restaurant name] --> latitude
            [restaurant name] --> longitude
    """
    ret_dict = {}
    ff = []
    location_lat_dict = {}
    location_long_dict = {}
    try:
        max_num = search_req(0)['total']   
    except KeyError:
        print(zip_code)
    if max_num < limit:
        max_num = limit + 1
    for i in range(0, max_num - limit, limit):
        req = search_req(i)
        if 'businesses' not in req.keys():
            continue
        req_businesses = req['businesses']
        for restaurant in req_businesses:
            name = restaurant['name']
            location = restaurant['location']
            try:
                if int(location['zip_code']) != zip_code:
                    continue
            except ValueError:
                continue
            if location:
                lat, long = get_location(restaurant)
                location_lat_dict[name] = lat
                location_long_dict[name] = long
            try:
                for dic in restaurant['categories']:
                    if dic['alias'] == 'hotdogs':
                        ff.append(name)
            except ValueError:
                ff += 0
            if 'price' in restaurant:
                ret_dict[name] = len(restaurant['price'])
    if ff == True:
        return ret_dict, ff
    if location == True:
        return location_lat_dict, location_long_dict
    return ret_dict

def get_mapping_data():
    names = []
    lats = []
    longs = []
    prices = []
    for elm in student_zips + non_student_zips:
        print(elm)
        search_lst[0] = "location=" + str(elm)
        na, la, lo, pr = get_mapping_data_helper(elm)
        names.extend(na)
        lats.extend(la)
        longs.extend(lo)
        prices.extend(pr)
    return [names, lats, longs, prices]

def get_mapping_data_helper(zip_code):
    names = []
    lats = []
    longs = []
    prices = []
    max_num = search_req(0)['total']
    for i in range(0, max_num - limit, limit):
        req = search_req(i)
        if 'businesses' not in req.keys():
            continue
        req_businesses = req['businesses']
        for restaurant in req_businesses:
            name = restaurant['name']
            location = restaurant['location']
            try:
                if int(location['zip_code']) != zip_code:
                    continue
            except ValueError:
                continue
            names.append(name)
            if location:
                lat, long = get_location(restaurant)
                lats.append(lat)
                longs.append(long)
            else:
                lats.append(0)
                longs.append(0)
            if 'price' in restaurant:
                prices.append(len(restaurant['price']))
            else:
                prices.append(100)
    return names, lats, longs, prices

def get_all_data():
    names = []
    lats = []
    longs = []
    prices = []
    rating = []
    review_count = []
    student_location = []
    for elm in student_zips + non_student_zips:
        search_lst[0] = "location=" + str(elm)
        na, la, lo, pr, ra, re, st = get_all_data_helper(elm)
        names.extend(na)
        lats.extend(la)
        longs.extend(lo)
        prices.extend(pr)
        rating.extend(ra)
        review_count.extend(re)
        student_location.extend(st)
    return [names, lats, longs, prices, rating, review_count, student_location]

def get_all_data_helper(zip_code):
    names = []
    lats = []
    longs = []
    prices = []
    rating = []
    review_count = []
    student_location = []
    max_num = search_req(0)['total']
    for i in range(0, max_num - limit, limit):
        req = search_req(i)
        if 'businesses' not in req.keys():
            continue
        req_businesses = req['businesses']
        for restaurant in req_businesses:
            name = restaurant['name']
            location = restaurant['location']
            try:
                if int(location['zip_code']) != zip_code:
                    continue
            except ValueError:
                continue
            names.append(name)
            if location:
                lat, long = get_location(restaurant)
                lats.append(lat)
                longs.append(long)
            else:
                lats.append(0)
                longs.append(0)
            if 'price' in restaurant:
                prices.append(len(restaurant['price']))
            else:
                prices.append(100)
            if 'rating' in restaurant:
                rating.append(restaurant['rating'])
            else:
                rating.append(-1)
            if 'review_count' in restaurant:
                review_count.append(restaurant['review_count'])
            else:
                review_count.append(-1)
            if zip_code in student_zips:
                student_location.append(True)
            else:
                student_location.append(False)
    return names, lats, longs, prices, rating, review_count, student_location 

def get_location(restaurant):
    """ Returns the latitude and longitude of a given restaurant """
    coordinates = restaurant['coordinates']
    return coordinates['latitude'], coordinates['longitude']

def write_zip_info():
    """ Writes information about the student and non student zip codes to 2 different .csv's """
    student_data_rest, student_data_prices = get_lst_prices(student_zips)
    non_student_data_rest, non_student_data_prices = get_lst_prices(non_student_zips)

    write_csv_2("test1.csv", "restaurants", "prices", student_data_rest, student_data_prices)
    write_csv_2("test2.csv", "restaurants", "prices", non_student_data_rest, non_student_data_prices)
    return student_data_prices, non_student_data_prices

def write_mapping_info():
    lst = get_mapping_data()
    names = np.array(lst[0])
    lats = np.array(lst[1])
    longs = np.array(lst[2])
    prices = np.array(lst[3])

    df = pd.DataFrame({
        'Restaurant Name' : names,
        'Latitude' : lats,
        'Longitude' : longs,
        'Prices': prices
    })
    df.to_csv('mapping_data', index=False)

def write_all_info():
    lst = get_all_data()
    names = np.array(lst[0])
    lats = np.array(lst[1])
    longs = np.array(lst[2])
    prices = np.array(lst[3])
    rating = np.array(lst[4])
    review_count = np.array(lst[5])
    student_location = np.array(lst[6])

    df = pd.DataFrame({
        'Restaurant Name' : names,
        'Latitude' : lats,
        'Longitude' : longs,
        'Prices' : prices,
        'Rating' : rating,
        'Review Count' : review_count,
        'Student Location?' : student_location
    })
    df.to_csv('all_data.csv', index=False)



def write_csv_2(file_name, name1, name2, lst1, lst2):
    """ Writes a .csv for 2 lists """
    arr1 = np.array(lst1)
    arr2 = np.array(lst2)

    df = pd.DataFrame({name1 : arr1, name2 : arr2})
    df.to_csv(file_name, index = False)
