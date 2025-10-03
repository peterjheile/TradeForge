#contains the runner class used to run each bot. 
#Each bot contains its own strategy and decisions/methodlogy for trading; however
#THE RUNNER CLASS HANDLES THE EXECUTION OF TRADES VIA THE ALPACA API (INCLUDING THE COLLECTION OF PRICE DATA/ACCOUNT INFO/ETC)
from core.decision import Signal, Decision
from core.alpaca import AlpacaAccount
from agents.ps_random_choices import RandomChoices
from utils.logger import BotLogger
from core.metadata import RunnerMetadata
from datetime import datetime, timedelta
import time



class Runner:

    def __init__(self, agent, symbol, interval=60, duration=None, log = True, logging_info = None, logging_folder = "logs"):

        #generate the id for this bot.runner instance
        timer = datetime.now()
        timer_str = timer.strftime("%Y-%m-%d_%H-%M-%S")
        self.id = f"{timer_str}_{type(agent).__name__}_{symbol}"

        #the agent/strategy this runner will execute
        self.agent = agent

        #this class contains the api keys and alpaca account information, along with the api trading instance bound to the corresponding account
        self.account = AlpacaAccount()

        #when the runner will stop working. None means it will run indefinitely
        self.expiration = (timer+timedelta(seconds=duration)) if duration else None
        
        #metadata for this runner/bot instance
        self.metadata = RunnerMetadata(
            runner_id = self.id,
            agent_type = type(agent).__name__,
            symbol=symbol,
            paper=self.account.paper,
            interval=interval,
            duration=duration,
            started_at=timer,
            log=log,
            logging_filepath = f"{logging_folder}/{self.id}.csv" if log else None,
            logging_fields = logging_info
        )

        #logger for this bot/runner isntance. If folder does not exist, it is made at user desired folder
        self.logger = BotLogger(fields = self.metadata.logging_fields, filepath = self.metadata.logging_filepath) if log else None
    
        





        


    def run(self):
        print("Runner Started. Press Ctrl+C to stop.")
        
        #run indefinitely or for the specified duration
        while (self.expiration == None) or (datetime.now() < self.expiration):

            decision = self.agent.generate_Decision(symbol=self.metadata.symbol, price_data=None)
            self._execute_trade(decision)
            time.sleep(self.metadata.interval)



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


bot = Runner(agent=RandomChoices(), symbol="BTCUSD", interval=10, duration=60)

bot.run()


                


#next up on my to do list is to create a custom Metrics collector class that will return the data to log
