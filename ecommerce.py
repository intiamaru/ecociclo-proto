#!/usr/local/bin/python3

import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
#from elastic_handler import insert_document

def main():
    #print('{} {}'.format(dataset['orders'])
    orders = get_orders()
    #print(json.dumps(orders[0]))
    #
    filter = "ciclo11"
    print("Ordenes en el filtro:",filter)
    print_orders(orders,tag=filter)


    # print("Deliveries")
    # print_deliveries(orders)

    print("Retrieving summary", filter)
    df = get_summary(tag=filter)
    df.to_csv('summary_{}.csv'.format(filter))
    df.to_json(orient='index')


def get_summary_json(filter):
    print("Retrieving summary", filter)
    df = get_summary(tag=filter)
    result = df.to_json(orient='index')
    return result

def get_summary_html(filter):
    print("Retrieving summary", filter)
    df = get_summary(tag=filter)
    result = df.to_html()
    return result

def get_orders():
    #TODO set secrets in config
    url = "https://4b08f6d64e878fd6cb6449b0a5800ab6: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@ecociclo.myshopify.com/admin/api/2020-04/orders.json"
    resp = requests.get(url)
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /admin/api/2020-04/orders.json {}'.format(resp.status_code))
    dataset = resp.json()
    return dataset['orders']

def dic_products():
    ps = get_products()
    result = {}
    for p in ps:
        p['sku'] = p['variants'][0]['sku']
        p['price'] = p['variants'][0]['price']
        id = p['sku']
        result[id] = p
    return result

def get_products():
    #TODO set secrets in config
    url = "https://4b08f6d64e878fd6cb6449b0a5800ab6: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@ecociclo.myshopify.com/admin/api/2020-04/products.json?limit=250"
    resp = requests.get(url)
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /admin/api/2020-04/products.json {}'.format(resp.status_code))
    dataset = resp.json()
    result = dataset['products']
    return result

def dic_inventory_items(ids):
    ii = get_inventory_items(ids)
    result = {}
    for i in ii:
        id = i['sku']
        result[id] = i
    return result

def get_inventory_items(ids):
    #TODO set secrets in config
    url = "https://4b08f6d64e878fd6cb6449b0a5800ab6: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@ecociclo.myshopify.com/admin/api/2020-04/inventory_items.json?ids={}&limit=250".format(ids)
    resp = requests.get(url)
    if resp.status_code != 200:
        # This means something went wrong.
        raise ApiError('GET /admin/api/2020-04/inventory_items.json {}'.format(resp.status_code))
    dataset = resp.json()
    response = dataset['inventory_items']

    return response

def save_orders(orders):
    for order in orders:
        insert_document("order", order)


def print_orders(orders, tag=None):
    gen = {}
    if tag:
        gen = (rs for rs in orders if (not rs["tags"] == "") and (tag in rs["tags"]) )
    else:
        gen = orders

    for order in gen:
        print_order(order)
        #print( json.dumps(order))

def print_order(order):

    #cabecera
    customer_info = ""
    if "customer" in order:
        customer_info = '{} {} - #{} @ {}'.format(order["customer"]["first_name"],order["customer"]["last_name"],order["customer"]["phone"],order["customer"]["email"])
    else:
        customer_info = "Orden Interna"
    print('\n{} {} - {}'.format(order["name"], order["tags"], customer_info) )

    #dirección entrega / recojo
    if "shipping_address" in order:
        print("Delivery: {} {} {} - #{}".format( order["shipping_address"]["address1"], order["shipping_address"]["address2"], order["shipping_address"]["city"], order["shipping_address"]["phone"]))
    else:
        print("Recojo: {}".format(order["shipping_lines"][0]["title"]))

    #notas
    if order["note"]:
        print("Notas: {}".format(order["note"]))

    #estado
    print("Info: {} : {}".format(order["gateway"],order["financial_status"]))


    #detalle
    items_list = []
    for item in order["line_items"]:
        #print("{} {} S/.{}".format( item["title"], item["quantity"], item["price"]) )
        item_dic ={}
        item_dic["title"] = item["title"]
        item_dic["quantity"] = item["quantity"]
        #item_dic["price"] = item["price"]
        items_list.append(item_dic)


    df = pd.DataFrame(items_list)
    #df = df[["title", "quantity"]]
    dfStyler = df.style.set_properties(**{'text-align': 'left'})
    dfStyler.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    with pd.option_context('display.colheader_justify','left'):
         print(df)

def print_deliveries(orders):
    for order in orders:
        #cabecera
        customer_info = ""
        if "customer" in order:
            customer_info = '{} {} - #{} @ {}'.format(order["customer"]["first_name"],order["customer"]["last_name"],order["customer"]["phone"],order["customer"]["email"])
        else:
            customer_info = "Orden Interna"
        print('\n{} {} - {}'.format(order["name"], order["tags"], customer_info) )

        #dirección entrega / recojo
        if "shipping_address" in order:
            print("Delivery: {} {} {} - #{}".format( order["shipping_address"]["address1"], order["shipping_address"]["address2"], order["shipping_address"]["city"], order["shipping_address"]["phone"]))
        else:
            print("Recojo: {}".format(order["shipping_lines"][0]["title"]))

        #notas
        if "note" in order:
            print("Notas: {}".format(order["notes"]))

        print("productos:", len(order["line_items"]) )



def get_summary(tag=None):

    dataset = []
    #products dic
    dproducts = dic_products()
    # print(json.dumps(dproducts))

    iis = []
    for key, product in dproducts.items():
        iis.append(str(product['variants'][0]['inventory_item_id']))
    ids = ','.join(iis)

    #inventory_items dic
    dinventory_items = dic_inventory_items(ids)
    # print(json.dumps(dinventory_items))

    orders = get_orders()
    filtered_orders = {}
    if tag:
        filtered_orders = (rs for rs in orders if (not rs["tags"] == "") and (tag in rs["tags"]) )
    else:
        filtered_orders = orders

    for order in filtered_orders:
        for item in order["line_items"]:
            #print("{} {} S/.{}".format( item["title"], item["quantity"], item["price"]) )
            item_dic ={}
            item_dic["order"] = order["name"]
            if "customer" in order:
                item_dic["customer"] = '{} {}'.format(order["customer"]["first_name"],order["customer"]["last_name"])
            item_dic["sku"] = item["sku"]
            sku = item["sku"]
            item_dic["vendor"] = item["vendor"]
            item_dic["title"] = item["title"]
            item_dic["quantity"] = item["quantity"]
            item_dic["price"] = dproducts[sku]["price"]
            item_dic["cost"] = dinventory_items[sku]["cost"]
            item_dic["line_price"] = item["quantity"] * float(dproducts[sku]["price"])
            item_dic["line_cost"] = item["quantity"] * float(dinventory_items[sku]["cost"])
            item_dic["tags"] = order["tags"]
            dataset.append(item_dic)

    print(json.dumps(dataset))
    df = pd.DataFrame(dataset)
    df = df[["order", "customer", "sku", "title", "quantity", "price", "cost", "line_price", "line_cost", "vendor"]]
    print(df)
    return df




if __name__ == '__main__':
    main()

