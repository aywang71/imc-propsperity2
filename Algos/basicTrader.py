from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string


class Trader:

    def calcPrice(self, order_depth):
        buy = order_depth.buy_orders
        sell = order_depth.sell_orders
        buy_weighted_sum = sum(price * quantity for price, quantity in buy.items())
        buy_total_quantity = sum(buy.values())
        buy_weighted_average = buy_weighted_sum / buy_total_quantity

        sell_weighted_sum = sum(price * quantity for price, quantity in sell.items())
        sell_total_quantity = sum(
            abs(quantity) for quantity in sell.values())  # use abs() to ensure quantities are positive
        sell_weighted_average = sell_weighted_sum / sell_total_quantity
        sell_weighted_average_pos = abs(sell_weighted_average)
        midpoint = (buy_weighted_average + sell_weighted_average_pos) / 2
        return midpoint
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        #TODO: Cannot hardcode position values, must paramterize as # products increases
        ame = state.position.get("AMETHYSTS", 0)
        ameLimit = 20
        star = state.position.get("STARFRUIT", 0)
        starLimit = 20
        print("positions: " + str(ame) + ", " + str(star))
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            # TODO: Cannot hardcode position values, need to paramterize them
            if product == "AMETHYSTS": #high-freqency
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                # Always midpoint at 10k due to stability
                acceptable_price = 10000
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                    len(order_depth.sell_orders)))

                i = 0
                while i < len(order_depth.sell_orders):
                    ask, ask_amount = list(order_depth.sell_orders.items())[i]
                    ask_amount = min(ask_amount, ameLimit - ame)
                    if int(ask) <= acceptable_price:
                        print("BUY", str(-ask_amount) + "x", ask)
                        orders.append(Order(product, ask, -ask_amount))
                        ame += ask_amount
                    i += 1

                """if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) <= acceptable_price:
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))"""
                ame = state.position.get("AMETHYSTS", 0)
                i = 0
                while i < len(order_depth.sell_orders):
                    bid, bid_amount = list(order_depth.buy_orders.items())[0]
                    bid_amount = min(-bid_amount, ame + ameLimit)
                    if int(bid) >= acceptable_price:
                        print("SELL", str(bid_amount) + "x", bid)
                        orders.append(Order(product, bid, -bid_amount))
                        ame -= bid_amount
                    i += 1
                """if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) >= acceptable_price:
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))"""

                result[product] = orders
            else:
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                #Calculate acceptable price as the midpoint between the medians of buy/sell
                acceptable_price = self.calcPrice(order_depth)
                print("Acceptable price : " + str(acceptable_price))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                    len(order_depth.sell_orders)))

                i = 0
                while i < len(order_depth.sell_orders):
                    ask, ask_amount = list(order_depth.sell_orders.items())[i]
                    ask_amount = min(-ask_amount, starLimit - star)
                    if int(ask) <= acceptable_price:
                        print("BUY", str(-ask_amount) + "x", ask)
                        orders.append(Order(product, ask, -ask_amount))
                        star += ask_amount
                    i += 1

                """if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))"""
                star = state.position.get("STARFRUIT", 0)

                i = 0
                while i < len(order_depth.sell_orders):
                    bid, bid_amount = list(order_depth.buy_orders.items())[0]
                    bid_amount = min(bid_amount, star + starLimit)
                    if int(bid) >= acceptable_price:
                        print("SELL", str(bid_amount) + "x", bid)
                        orders.append(Order(product, bid, -bid_amount))
                        star -= bid_amount
                    i += 1
                #TODO: Put in an order for whatever is remaining on buy/sell limits to buy at very good price and see if anyone matches it
                """if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))"""

                result[product] = orders

        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = state.traderData
        print(result)

        # Sample conversion request. Check more details below.
        conversions = 1
        return result, conversions, traderData