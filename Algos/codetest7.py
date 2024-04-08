from datamodel import OrderDepth, UserId, TradingState, Order, Listing, Trade, Observation, ConversionObservation
from typing import List, Dict

class Trader:

    def __init__(self):
        self.position_limits = {
            "AMETHYSTS": 20,
            "STARFRUIT": 20
        }

        self.risk_limits = {
            "AMETHYSTS": 0.1,  # Maximum 10% of portfolio risk per trade
            "STARFRUIT": 0.15  # Maximum 15% of portfolio risk per trade
        }

    def calculate_portfolio_value(self, state: TradingState) -> float:
        total_value = 0
        for product, position in state.position.items():
            listing = state.listings.get(product)
            if listing:
                total_value += position #* listing.denomination
        return total_value

    def calculate_position_risk(self, product: str, price: int, quantity: int, state: TradingState) -> float:
        listing = state.listings.get(product)
        print("Inside calculate_position_risk")
        print(listing)
        if listing:
            position_value = price * quantity #* listing.denomination
            portfolio_value = self.calculate_portfolio_value(state)
            return position_value / portfolio_value
        else:
            return 0

    def validate_order(self, order: Order, state: TradingState) -> bool:
        product = order.symbol
        position_limit = self.position_limits.get(product, 0)
        if product in state.position:
            current_position = state.position[product]
            proposed_position = current_position + order.quantity
            if abs(proposed_position) > position_limit:
                return False
        return True

    def run(self, state: TradingState):
        # Error handling
        if state is None:
            return {}, 0, ""

        # Strategy logic
        result = {}
        conversions = 0
        trader_data = state.traderData

        print(trader_data)

        for product, order_depth in state.order_depths.items():
            print(product)
            print(state.position)
            if product in state.position:
                current_position = state.position[product]

                # Risk management
                risk_limit = self.risk_limits.get(product, 0)

                print("Risk Limit : " + str(risk_limit))
                for price, quantity in order_depth.buy_orders.items(): #TODO this for loop only looks at buy orders, there is no sell
                    print(price)
                    print(quantity)
                    if quantity > 0:
                        position_risk = self.calculate_position_risk(product, price, quantity, state)
                        if position_risk > risk_limit:
                            # Skip this price level to avoid exceeding risk limit
                            continue

                    if len(result.get(product, [])) == 0:
                        # Only place one order per product per iteration
                        best_bid, best_bid_amount = price, quantity
                        if current_position >= 0:
                            if best_bid_amount > 0:
                                # Place buy order
                                order_quantity = min(best_bid_amount, self.position_limits[product] - current_position)
                                order = Order(product, best_bid, -order_quantity)
                                #if self.validate_order(order, state):
                                result[product] = [order]
                                break
                        else: #TODO: Only looking at buy_orders
                            # Check for sell opportunity
                            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                            if best_ask_amount < 0:
                                # Place sell order
                                order_quantity = min(-best_ask_amount, abs(current_position))
                                order = Order(product, best_ask, order_quantity)
                                #if self.validate_order(order, state):
                                result[product] = [order]
                                break
            else: # if we do not own any of the product, we take a half position initallity to prevent the algo from stalling
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                order_quantity = min(best_ask_amount, self.position_limits[product] // 2)
                order = Order(product, best_ask, -order_quantity)
                #if self.validate_order(order, state):
                result[product] = [order]

        return result, conversions, trader_data
