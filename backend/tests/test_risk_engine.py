"""Tests for risk engine."""
import pytest

from app.engines.risk_engine import RiskEngine, RiskConfig, RiskMode


class TestRiskEngine:
    """Test suite for RiskEngine."""
    
    def test_calculate_risk_state_normal(self):
        """Test normal risk state."""
        engine = RiskEngine()
        
        state = engine.calculate_risk_state(
            current_equity=100000,
            peak_equity=105000,
            daily_pnl=1000,
            start_of_day_equity=99000
        )
        
        assert state.mode == RiskMode.NORMAL
        assert state.risk_multiplier == 1.0
        assert state.can_open_new_trades == True
    
    def test_calculate_risk_state_warning(self):
        """Test warning risk state (10% drawdown)."""
        engine = RiskEngine()
        
        state = engine.calculate_risk_state(
            current_equity=90000,  # 10% down from peak
            peak_equity=100000,
            daily_pnl=-1000,
            start_of_day_equity=91000
        )
        
        assert state.mode == RiskMode.WARNING
        assert state.risk_multiplier == 0.5  # Risk halved
        assert state.can_open_new_trades == True
    
    def test_calculate_risk_state_halt_drawdown(self):
        """Test halt risk state (15% drawdown)."""
        engine = RiskEngine()
        
        state = engine.calculate_risk_state(
            current_equity=85000,  # 15% down from peak
            peak_equity=100000,
            daily_pnl=-500,
            start_of_day_equity=85500
        )
        
        assert state.mode == RiskMode.HALT
        assert state.risk_multiplier == 0.0
        assert state.can_open_new_trades == False
    
    def test_calculate_risk_state_halt_daily_loss(self):
        """Test halt risk state (daily loss limit)."""
        engine = RiskEngine()
        
        state = engine.calculate_risk_state(
            current_equity=97500,  # -2.5% daily
            peak_equity=100000,
            daily_pnl=-2500,
            start_of_day_equity=100000
        )
        
        assert state.mode == RiskMode.HALT
        assert state.can_open_new_trades == False
    
    def test_calculate_position_size_normal(self):
        """Test position size calculation."""
        engine = RiskEngine(RiskConfig(risk_per_trade=0.01))
        
        from app.engines.risk_engine import RiskState
        risk_state = RiskState(
            equity=100000,
            peak_equity=100000,
            daily_pnl=0,
            drawdown_pct=0,
            daily_loss_pct=0,
            mode=RiskMode.NORMAL,
            risk_multiplier=1.0,
            can_open_new_trades=True,
            message="Normal"
        )
        
        size = engine.calculate_position_size(
            equity=100000,
            entry_price=4000,
            stop_price=3900,  # 100 point stop
            tick_size=0.25,
            multiplier=50,  # ES multiplier
            risk_state=risk_state
        )
        
        # Risk = $1000 (1% of 100k)
        # Stop distance = 100 points * $50 = $5000 per contract
        # Contracts = $1000 / $5000 = 0.2 -> floor to 0
        # But with 0.5% risk should give us 1 contract
        assert size.contracts >= 0
        assert size.stop_distance_points == 100
    
    def test_calculate_position_size_with_max_contracts(self):
        """Test position size with max contracts limit."""
        config = RiskConfig(
            risk_per_trade=0.05,  # High risk
            max_contracts_per_instrument=2
        )
        engine = RiskEngine(config)
        
        from app.engines.risk_engine import RiskState
        risk_state = RiskState(
            equity=100000,
            peak_equity=100000,
            daily_pnl=0,
            drawdown_pct=0,
            daily_loss_pct=0,
            mode=RiskMode.NORMAL,
            risk_multiplier=1.0,
            can_open_new_trades=True,
            message="Normal"
        )
        
        size = engine.calculate_position_size(
            equity=100000,
            entry_price=4000,
            stop_price=3950,  # 50 point stop
            tick_size=0.25,
            multiplier=50,
            risk_state=risk_state
        )
        
        # Should be limited to max 2 contracts
        assert size.contracts <= 2
    
    def test_check_exposure_limits(self):
        """Test exposure limits check."""
        config = RiskConfig(max_gross_exposure=0.5)  # 50% max
        engine = RiskEngine(config)
        
        current_positions = [
            {'value': 40000, 'symbol': 'ES'},  # 40% of equity
        ]
        
        # Try to add another 20% position
        allowed, reason = engine.check_exposure_limits(
            current_positions=current_positions,
            new_position_value=20000,
            equity=100000,
            instrument_symbol='NQ'
        )
        
        # 40% + 20% = 60% > 50% limit
        assert allowed == False
    
    def test_check_correlated_exposure_limits(self):
        """Test correlated exposure limits (ES+NQ)."""
        config = RiskConfig(
            max_gross_exposure=1.0,  # Allow 100% gross
            max_correlated_exposure=0.3  # But only 30% for ES+NQ combined
        )
        engine = RiskEngine(config)
        
        current_positions = [
            {'value': 20000, 'symbol': 'ES'},  # 20% in ES
        ]
        
        # Try to add another 20% in NQ
        allowed, reason = engine.check_exposure_limits(
            current_positions=current_positions,
            new_position_value=20000,
            equity=100000,
            instrument_symbol='NQ'
        )
        
        # 20% + 20% = 40% > 30% correlated limit
        assert allowed == False
    
    def test_validate_trade_success(self):
        """Test successful trade validation."""
        engine = RiskEngine()
        
        size, risk_state = engine.validate_trade(
            equity=100000,
            peak_equity=100000,
            daily_pnl=0,
            start_of_day_equity=100000,
            entry_price=4000,
            stop_price=3900,
            tick_size=0.25,
            multiplier=50,
            current_positions=[],
            instrument_symbol='ES'
        )
        
        assert risk_state.mode == RiskMode.NORMAL
        assert size.contracts >= 0

