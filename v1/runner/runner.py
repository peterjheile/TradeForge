#contains the runner class used to run each bot. 
#Each bot contains its own strategy and decisions/methodlogy for trading; however
#THE RUNNER CLASS HANDLES THE EXECUTION OF TRADES VIA THE ALPACA API (INCLUDING THE COLLECTION OF PRICE DATA/ACCOUNT INFO/ETC)
from core.decision import Signal, Decision
from core.alpaca import AlpacaAccount
from agents.ps_random_choices import RandomChoicesAgent
from utils.logger import BotLogger
from core.metadata import RunnerMetadata
from utils.timer import Timer
from utils.id_generator import IDFactory
from agents.ps_moving_average import MovingAverageAgent



class Runner:

    def __init__(self, agent, symbol, interval=60, duration=None, log = True, logging_info = None, logging_folder = "logs"):

        #custom timer for the runner. Pretty basic but encapsles some useful functionality for the runner
        self.timer = Timer(interval, duration)

        #generate the id for this bot.runner instance
        self.id = IDFactory.generate_bot_id(agent=agent, symbol=symbol, timestamp=self.timer.id)

        #the associated symbol
        #NOTE: I may add multi-symbolation later for each runner but for now each runner/bot can only trade on once stock/crypto or whatever chosen
        self.symbol = symbol

        #the agent/strategy this runner will execute
        self.agent = agent

        #this class contains the api keys and alpaca account information, along with the api trading instance bound to the corresponding account
        self.account = AlpacaAccount()

        #when the runner will stop working. None means it will run indefinitely
        self.expiration = self.timer.end_time
        
        #metadata for this runner/bot instance
        self.metadata = RunnerMetadata(
            runner_id = self.id,
            agent_type = type(agent).__name__,
            symbol=symbol,
            paper=self.account.paper,
            interval=interval,
            duration=duration,
            started_at=self.timer.start_time,
            log=log,
            logging_filepath = f"{logging_folder}/{self.id}.csv" if log else None,
            logging_fields = logging_info
        )

        #logger for this bot/runner isntance. If folder does not exist, it is made at user desired folder
        self.logger = BotLogger(fields = self.metadata.logging_fields, filepath = self.metadata.logging_filepath) if log else None

        #NOTE: I need to make some form of cross validation with the logger and the field metadata, as it stands the logger just "trusts" that
        #that the given fields are valid fields (meaning I have the use the validated fields from the metadata; which may not be convenient sometimes).
        # Also how the fildpath is created seems off, I need it generated in the logger





        


    def run(self):
        print("Runner Started. Press Ctrl+C to stop.")
        
        #run indefinitely or for the specified duration
        while (self.expiration == None) or (self.timer.current_time() < self.expiration):

            decision = self.agent.generate_decision(symbol=self.metadata.symbol, price_data=None)
            self._execute_trade(decision)
            self.timer.sleep_interval() #sleep at the timer's given interval (i.e. the interval given on runner init) if no parameter is given
            


    def _execute_trade(self, decision: Decision):
        sym = decision.symbol
        if decision.signal == Signal.BUY:
            try:
                order = self.account.api.submit_order(
                    symbol=sym,
                    # qty=.1,                    # MVP: fixed size
                    notional=100,               # MVP: fixed dollar amount
                    side="buy",
                    type="market",
                    time_in_force="gtc"
                )
                

                self.logger.log(self.metadata.logging_fields)

            except Exception as e:
                self.logger.log(f"[ERROR] BUY {sym}: {e}")

        elif decision.signal == Signal.SELL:
            try:
                # MVP choice: just liquidate whatever you have.
                # If flat, Alpaca will raise; we swallow it and move on.
                self.account.api.close_position(sym)
                self.logger.log(self.metadata.logging_fields)

            except Exception as e:
                self.logger.log(f"[INFO] No position to close for {sym}: {e}")
        else:  # Signal.HOLD


            self.logger.log("[HOLD]")





    def _list_positions(self):
        print(self.api.list_positions())

    def _sell_position(self, symbol):
        self.api.close_position(symbol)

    def temp_data_getter(self):
        return self.account.api.get_crypto_bars("BTC/USD", "1Min", limit=max(self.agent.short_window, self.agent.long_window)).df



agent = MovingAverageAgent()
bot = Runner(agent=agent, symbol="BTCUSD", interval=5, duration=15)
print(bot.temp_data_getter())


# bot.run()


                


#next up on my to do list is to create a custom Metrics collector class that will return the data to log
