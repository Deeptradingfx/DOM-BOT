
"""
Made by Rodrigo Calderano Barbacovi
"""

import datetime
import zmq
import gspread
import requests
import sys
import re
import time
import json
from unicodedata import normalize
from oauth2client.service_account import ServiceAccountCredentials

SOCKET_LOCAL_HOST = "tcp://localhost:5555"

# WAIT_TIME: secs * min
WAIT_TIME = 10 * 1


def meta_trader_connector():
    """
        Establish a connection between MetaTrader 5 and Python through local Sockets with ZeroMQ
        Parameters: null
        Return: socket
    """
    print("Connecting to MetaTrader...")
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(SOCKET_LOCAL_HOST)
    return socket


def meta_trader_get_values(socket, data):
    """
        Send data to MetaTrader
        Parameters: socket, data: ('RATES|PETR4')
        Return: stock data:
        stock data: (bid, ask, buy_volume, sell_volume, tick_volume, real_volume, buy_volume_market, sell_volume_market)
    """
    print("Getting data from MetaTrader...")
    try:
        socket.send_string(data)
        msg = socket.recv_string()
        return msg

    except zmq.Again as e:
        print("Something went wrong: " + str(e))


def google_sheets_connector():
    """
        Connect to google sheets
        Parameters: null
        Return: sheet
    """
    print("Connecting to Google Sheets")
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
    client = gspread.authorize(credentials)
    sheet = client.open('backend').sheet1
    return sheet


def get_orders_from_sheet(sheet):
    """
        Get orders from Google Sheets
        Parameters: sheet
        Return: orders list
        order: (stock name, entry, stop gain, stop partial, stop loss, flag (already bought?))
    """
    print("Getting data from Google Sheets...")
    my_orders = []
    for row in range(100):
        order = sheet.row_values(row + 2)
        if order[0] != '-':
            my_orders.append(order)
            continue
        break
    print("My orders: " + str(my_orders) + "\n")
    return my_orders


def manual_module(stock_ideal, stock_current):
    print('Checking if it is time to buy: ' + stock_ideal[0])
    """
        Compare the ideal stock values with the current value
        Parameters: stock_ideal, stock_current
        stock_ideal: (stock name, entry, stop gain, stop partial, stop loss, flag (already bought?))
        stock_current: (bid, ask, buy_volume, sell_volume, tick_volume,
                        real_volume, buy_volume_market, sell_volume_market)
        Return:
    """
    # TODO FINALIZAR CONSEQUENCIA CHECAR FLAG ETC

    if stock_ideal[1] < stock_current[1]:
        print('Yeap, it is time to buy: ' + stock_ideal[0])
    else:
        print("Nah, it's not the time to buy: " + stock_ideal[0] + "\n")


if __name__ == '__main__':
    print("----------------")
    print("Iniciando script")
    print("----------------")
    timeNow = datetime.datetime.now()

    # Google Sheets:
    my_sheet = google_sheets_connector()

    # Meta Trader:
    meta_trader_socket = meta_trader_connector()

    while True:
        orders = get_orders_from_sheet(my_sheet)
        for each_order in orders:
            # Send RATES command to ZeroMQ MT5
            mt_response = meta_trader_get_values(meta_trader_socket, "RATES|" + each_order[0]).split(',')
            manual_module(each_order, mt_response)

        time.sleep(WAIT_TIME)
        print("\n\n\n\n")
