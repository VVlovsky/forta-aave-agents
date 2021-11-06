from forta_agent import FindingSeverity, FindingType, create_block_event
from agent import provide_handle_block, MARKET, TOKEN_1, TOKEN_2


class Web3Mock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.eth = EthMock(exchange_rate_1, exchange_rate_2)


class EthMock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.contract = ContractMock(exchange_rate_1, exchange_rate_2)


class ContractMock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.functions = FunctionsMock(exchange_rate_1, exchange_rate_2)

    def __call__(self, *args, **kwargs):
        return self


class FunctionsMock:
    def __init__(self, exchange_rate_1, exchange_rate_2):
        self.exchange_rate_1 = exchange_rate_1
        self.exchange_rate_2 = exchange_rate_2

    def getAssetsPrices(self, **_):
        return self

    def call(self, **_):
        return self.exchange_rate_1, self.exchange_rate_2


class TestExchangeRateAgent:
    block_event = create_block_event({
        'block': {
            'number': 0
        }
    })

    def test_returns_zero_returns_finding_if_ex_rate_does_not_drop(self):
        w3 = Web3Mock(8, 10)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0
        w3 = Web3Mock(8.5, 10)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0

    def test_returns_returns_finding_if_ex_rate_drops_with_severity_high(self):
        w3 = Web3Mock(9, 10)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0
        w3 = Web3Mock(8, 10)
        findings = provide_handle_block(w3)(self.block_event)
        for finding in findings:
            assert finding.alert_id == 'AAVE-EXR'
            assert finding.description == f'{TOKEN_1}/{TOKEN_2} Exchange Rate Goes Down'
            assert finding.name == 'Aave Exchange Rate Down'
            assert finding.severity == FindingSeverity.High
            assert finding.type == FindingType.Info
            assert finding.metadata['1st_token'] == TOKEN_1
            assert finding.metadata['2nd_token'] == TOKEN_2
            assert finding.metadata['difference'] == 9 / 10 - 8 / 10
            assert finding.metadata['market'] == MARKET

    def test_returns_returns_finding_if_ex_rate_drops_with_severity_medium(self):
        w3 = Web3Mock(9, 10)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0
        w3 = Web3Mock(8.9, 10)
        findings = provide_handle_block(w3)(self.block_event)
        for finding in findings:
            assert finding.alert_id == 'AAVE-EXR'
            assert finding.description == f'{TOKEN_1}/{TOKEN_2} Exchange Rate Goes Down'
            assert finding.name == 'Aave Exchange Rate Down'
            assert finding.severity == FindingSeverity.Medium
            assert finding.type == FindingType.Info
            assert finding.metadata['1st_token'] == TOKEN_1
            assert finding.metadata['2nd_token'] == TOKEN_2
            assert finding.metadata['difference'] == 9 / 10 - 8.9 / 10
            assert finding.metadata['market'] == MARKET

    def test_returns_returns_finding_if_ex_rate_drops_with_severity_critical(self):
        w3 = Web3Mock(9, 10)
        findings = provide_handle_block(w3)(self.block_event)
        assert len(findings) == 0
        w3 = Web3Mock(5, 10)
        findings = provide_handle_block(w3)(self.block_event)
        for finding in findings:
            assert finding.alert_id == 'AAVE-EXR'
            assert finding.description == f'{TOKEN_1}/{TOKEN_2} Exchange Rate Goes Down'
            assert finding.name == 'Aave Exchange Rate Down'
            assert finding.severity == FindingSeverity.Critical
            assert finding.type == FindingType.Info
            assert finding.metadata['1st_token'] == TOKEN_1
            assert finding.metadata['2nd_token'] == TOKEN_2
            assert finding.metadata['difference'] == 9 / 10 - 5 / 10
            assert finding.metadata['market'] == MARKET
