#from amazon.api import AmazonAPI
import credentials
import push_credentials
from pprint import pprint
from wishlist.core import Wishlist
import pickle
from pathlib import Path
from datetime import datetime
from pushover import Client

#setup
wishlist_1 = "3C4OZASG6ZZ4R"

#authenticate
#amazon = AmazonAPI(credentials.access_key, credentials.secret_key, credentials.ass_tag)
client = Client(push_credentials.push_user, api_token=push_credentials.push_token)

def money_format(money):
    return str('${:,.2f}'.format(float(money)))

def percent_format(new_number,old_number):
    return str("{0:.0f}%".format(new_number - old_number))

def time_format(time):
    return str(str(time.month) +"/"+ str(time.day)+"/"+ str(time.year)+" "+str(time.time().strftime('%I:%M:%S %p')))

def t_delta(duration):
    if duration == 0:
        return str(0)
    else:
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return str(hours)+":"+str(minutes)+":"+str(seconds)

def get_wishlist(wishlist_id):
    #return list of strings
    wish_list_dict = {}
    w = Wishlist(wishlist_id)
    for n,item in enumerate(w):
        timestamp = datetime.now()
        wish_list_dict[item.a_uuid] = {}
        wish_list_dict[item.a_uuid]['pricing_data'] = {}
        wish_list_dict[item.a_uuid]['ASIN'] = item.a_uuid
        wish_list_dict[item.a_uuid]['title'] = item.title
        wish_list_dict[item.a_uuid]['current_price'] = item.price
        wish_list_dict[item.a_uuid]['pricing_data'][timestamp] = item.price
        wish_list_dict[item.a_uuid]['source'] = item.source
        wish_list_dict[item.a_uuid]['url'] = item.url
        wish_list_dict[item.a_uuid]['timestamp'] = datetime.now()

    return wish_list_dict

def update_product_details(Item):
    product = amazon.lookup(ItemId=item)

def send_message(status,time_delta,price_delta,percent_delta,item_dictionary):
    print("sending message")
    print("Title: "+status)
    message = "Item: "+item_dictionary['title']+"\nPrice: "+money_format(item_dictionary['current_price'])+"\nTime Delta: "+t_delta(time_delta)+ \
    "\nPrice Delta: "+money_format(price_delta)+ \
    "\nPercent Delta: "+percent_delta+ \
    "\nLink: "+item_dictionary['url']

    print("Message: "+message)
    print()
    client.send_message(message, title=status)

def compare_pricing(current_wishlist,price_details):
    for current_item in current_wishlist: #check to see current WL items are in historical data
        if current_item not in price_details: #if current ASIN is not in the price_details dictionary
            print(current_item+" has been added to tracking")
            price_details[current_item] = current_wishlist[current_item] #add new key with information
        #else: remove entry if not on current wishlist?

    for current_item in current_wishlist: #for each item in wishlist
        for historical_item in price_details: #for each item in old dict
            if current_item == historical_item: #find match between two dictionaries with ASIN as keys

                if current_wishlist[current_item]['current_price'] > price_details[historical_item]['current_price']:
                    #PRICE INCREASE
                    timestamp = datetime.now() #new timestamp
                    time_delta = timestamp - price_details[historical_item]['timestamp'] #calculate time since change
                    price_delta = current_wishlist[current_item]['current_price'] - price_details[historical_item]['current_price']  #calculate price change
                    percent_delta = percent_format(current_wishlist[current_item]['current_price'], price_details[historical_item]['current_price'])
                    percent_delta_float = ((current_wishlist[current_item]['current_price'] - price_details[historical_item]['current_price'])/price_details[historical_item]['current_price'])*100
                    print("PERCENT DELTA FLOAT")
                    print(percent_delta_float)
                    if percent_delta_float > 4: #if price change is greater than a dollar

                        if price_details[historical_item]['current_price'] == 0: #if price is up from 0 - back in stock
                            #item is back in stock

                            price_details[historical_item]['pricing_data'][timestamp] = current_wishlist[current_item]['current_price'] #document time
                            price_details[historical_item]['current_price'] = current_wishlist[current_item]['current_price'] #set current_price key
                            price_details[historical_item]['timestamp'] = timestamp #set timestamp key

                            send_message("BACK IN STOCK",time_delta,price_delta,percent_delta,price_details[historical_item])
                            print("Price has gone up on "+current_wishlist[current_item]['ASIN'])

                        else: #if old price was anything but 0 (not indicating that product is out of stock)

                            price_details[historical_item]['pricing_data'][timestamp] = current_wishlist[current_item]['current_price'] #document time
                            price_details[historical_item]['current_price'] = current_wishlist[current_item]['current_price'] #set current_price key
                            price_details[historical_item]['timestamp'] = timestamp #set timestamp key

                            send_message("AMAZON INCREASE",time_delta,price_delta,percent_delta,price_details[historical_item])
                            print("Price has gone up on "+current_wishlist[current_item]['ASIN'])

                if current_wishlist[current_item]['current_price'] < price_details[historical_item]['current_price']:
                    #PRICE DECREASE
                    timestamp = datetime.now() #new timestamp
                    time_delta = timestamp - price_details[historical_item]['timestamp'] #calculate time since change
                    price_delta = current_wishlist[current_item]['current_price'] - price_details[historical_item]['current_price']#calculate price change
                    percent_delta = percent_format(current_wishlist[current_item]['current_price'], price_details[historical_item]['current_price'])
                    percent_delta_float = ((current_wishlist[current_item]['current_price'] - price_details[historical_item]['current_price'])/price_details[historical_item]['current_price'])*100
                    print("PERCENT DELTA FLOAT")
                    print(percent_delta_float)
                    
                    if percent_delta_float < -4: #if delta is lower than -1 (more of a discount would be -2)

                        if current_wishlist[current_item]['current_price'] == 0: #if product has dropped to 0

                            price_details[historical_item]['pricing_data'][timestamp] = current_wishlist[current_item]['current_price'] #document time
                            price_details[historical_item]['current_price'] = current_wishlist[current_item]['current_price'] #set current_price key
                            price_details[historical_item]['timestamp'] = timestamp #set timestamp key

                            send_message("OUT OF STOCK",time_delta,price_delta,percent_delta,price_details[historical_item])
                            print("price has gone down on "+current_wishlist[current_item]['ASIN'])

                        else: # if decrease is a normal drop

                            price_details[historical_item]['pricing_data'][timestamp] = current_wishlist[current_item]['current_price'] #document time
                            price_details[historical_item]['current_price'] = current_wishlist[current_item]['current_price'] #set current_price key
                            price_details[historical_item]['timestamp'] = timestamp #set timestamp key

                            send_message("AMAZON DECREASE",time_delta,price_delta,percent_delta,price_details[historical_item])
                            print("price has gone down on "+current_wishlist[current_item]['ASIN'])

                if current_wishlist[current_item]['current_price'] == price_details[historical_item]['current_price']:
                    #NO PRICE CHANGE
                    percent_delta = percent_format(current_wishlist[current_item]['current_price'], price_details[historical_item]['current_price'])
                    #print("price has not changed on "+current_wishlist[current_item]['ASIN'])
                    #send_message("SAME",0,0,percent_delta,price_details[historical_item])

price_file = Path("./price_details.dict")
if price_file.is_file():
#pricing import
    pickle_in = open("price_details.dict","rb")
    price_details = pickle.load(pickle_in)
else:
    f=open("price_details.dict","w+") #create file
    f.close()
    price_details = {} #create price_details dict and variables

    pickle_out = open("price_details.dict","wb") #open file
    pickle.dump(price_details, pickle_out) #save price_details dict to file
    pickle_out.close()

#get wishlist
current_wishlist = get_wishlist(wishlist_1) #get current wishlist and pricing

compare_pricing(current_wishlist,price_details) #compare prices to old, send messages

#save dictionary
pickle_out = open("price_details.dict","wb")
pickle.dump(price_details, pickle_out)
pickle_out.close()

timestamp = datetime.now()
print(str(timestamp)+" done")
