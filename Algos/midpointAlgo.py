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

                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) <= acceptable_price:
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        print("Order limits: " + str(-best_ask_amount) + " " + str(ameLimit - ame))
                        orders.append(Order(product, best_ask, min(-best_ask_amount, ameLimit - ame)))

                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) >= acceptable_price:
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        print("Order limits: " + str(-best_bid_amount) + " " + str(-ame - ameLimit))
                        orders.append(Order(product, best_bid, max(-best_bid_amount, -ame - ameLimit)))

                result[product] = orders
            else:
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                #Calculate acceptable price as the midpoint between the medians of buy/sell
                acceptable_price = self.calcPrice(order_depth)
                #print("Acceptable price : " + str(acceptable_price))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                    len(order_depth.sell_orders)))

                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if int(best_ask) < acceptable_price:
                        print("BUY", str(-best_ask_amount) + "x", best_ask)

                        print("Order limits: " + str(-best_ask_amount) + " " + str(starLimit - star))
                        orders.append(Order(product, best_ask, min(-best_ask_amount, starLimit - star)))

                #TODO: Put in an order for whatever is remaining on buy/sell limits to buy at very good price and see if anyone matches it
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if int(best_bid) > acceptable_price:
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        print("Order limits: " + str(-best_bid_amount) + " " + str(-star - starLimit))
                        orders.append(Order(product, best_bid, max(-best_bid_amount, -star - starLimit)))

                result[product] = orders

        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = state.traderData
        print(result)

        # Sample conversion request. Check more details below.
        conversions = 1
        return result, conversions, traderData