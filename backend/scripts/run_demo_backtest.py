"""Run a demo backtest with sample data."""
import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import BacktestRun
from app.schemas import BacktestConfig
from app.engines.backtest_engine import BacktestEngine


def run_demo_backtest():
    """Run a demo backtest on ES and NQ."""
    db = SessionLocal()
    
    print("Creating demo backtest configuration...")
    
    # Configure backtest
    config = BacktestConfig(
        instruments=["ES", "NQ"],
        start_date=date(2023, 1, 3),
        end_date=date(2023, 3, 31),
        initial_capital=100000.0,
        atr_period=20,
        ma_period=50,
        ma_slope_period=10,
        breakout_period=20,
        exit_period=10,
        stop_atr_multiple=2.0,
        cooldown_days=3,
        risk_per_trade=0.06,  # 6% - appropriate for futures
        max_contracts_per_instrument=5,
        max_gross_exposure=5.0,  # 500% - futures use leverage
        max_correlated_exposure=4.0,  # 400%
        slippage_ticks=1.0,
        commission_per_contract=2.50,
        entry_timing="next_open",
        drawdown_warning_pct=0.10,
        drawdown_halt_pct=0.15,
        daily_loss_limit_pct=0.02
    )
    
    # Create backtest run
    backtest_run = BacktestRun(
        name="Demo Backtest - ES & NQ Q1 2023",
        description="Demonstration backtest using sample data for ES and NQ futures",
        start_date=config.start_date,
        end_date=config.end_date,
        config=config.model_dump(mode='json'),  # Use JSON serialization mode
        initial_capital=config.initial_capital,
        status="pending"
    )
    
    db.add(backtest_run)
    db.commit()
    db.refresh(backtest_run)
    
    print(f"Created backtest run #{backtest_run.id}")
    print("Running backtest...")
    
    # Run backtest
    engine = BacktestEngine(db)
    try:
        engine.run_backtest(backtest_run, config)
        
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Status: {backtest_run.status}")
        print(f"Initial Capital: ${backtest_run.initial_capital:,.2f}")
        
        # Handle None values gracefully
        if backtest_run.final_equity is not None:
            print(f"Final Equity: ${backtest_run.final_equity:,.2f}")
        else:
            print("Final Equity: N/A")
            
        if backtest_run.total_return is not None:
            print(f"Total Return: {backtest_run.total_return:.2%}")
        else:
            print("Total Return: N/A")
            
        if backtest_run.cagr is not None:
            print(f"CAGR: {backtest_run.cagr:.2%}")
        else:
            print("CAGR: N/A")
            
        if backtest_run.sharpe_ratio is not None:
            print(f"Sharpe Ratio: {backtest_run.sharpe_ratio:.2f}")
        else:
            print("Sharpe Ratio: N/A")
            
        if backtest_run.sortino_ratio is not None:
            print(f"Sortino Ratio: {backtest_run.sortino_ratio:.2f}")
        else:
            print("Sortino Ratio: N/A")
            
        if backtest_run.max_drawdown is not None:
            print(f"Max Drawdown: {backtest_run.max_drawdown:.2%}")
        else:
            print("Max Drawdown: N/A")
            
        if backtest_run.max_drawdown_duration is not None:
            print(f"Max DD Duration: {backtest_run.max_drawdown_duration} days")
        else:
            print("Max DD Duration: N/A")
            
        if backtest_run.total_trades is not None:
            print(f"Total Trades: {backtest_run.total_trades}")
        else:
            print("Total Trades: 0")
            
        if backtest_run.win_rate is not None:
            print(f"Win Rate: {backtest_run.win_rate:.2%}")
        else:
            print("Win Rate: N/A")
            
        if backtest_run.profit_factor is not None:
            print(f"Profit Factor: {backtest_run.profit_factor:.2f}")
        else:
            print("Profit Factor: N/A")
            
        print("="*60)
        
        # If no results, explain why
        if backtest_run.final_equity is None:
            print("\n⚠️  No backtest results generated.")
            print("Possible reasons:")
            print("  - Not enough data (need 60+ bars for MA(50))")
            print("  - No valid signals generated")
            print("  - Check backend logs for details")
            
            if backtest_run.error_message:
                print(f"\nError: {backtest_run.error_message}")
        
    except Exception as e:
        print(f"\nError running backtest: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    run_demo_backtest()

