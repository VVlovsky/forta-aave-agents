import json
import eth_abi
from eth_utils import event_abi_to_log_topic
from forta_agent import create_transaction_event
from agent import handle_transaction
from src.constants import GOVERNANCE_PROPOSAL_EXECUTED_ABI, AAVE_GOVERNANCE_V2_MAINNET


class TestAaveGovernanceAgent:

    def test_returns_empty_findings_if_address_is_wrong(self):
        # filler contains random data, it is necessary to call filter_log() function
        filler = eth_abi.encode_abi(["address"], [AAVE_GOVERNANCE_V2_MAINNET])
        topics = [event_abi_to_log_topic(json.loads(GOVERNANCE_PROPOSAL_EXECUTED_ABI)), filler]
        tx_event = create_transaction_event({
            'receipt': {
                'logs': [
                    {'topics': topics,
                     'data': filler,
                     'address': "0x1010101010101010101010101010101010101010"}, ]},

        })
        findings = handle_transaction(tx_event)
        assert len(findings) == 0

    def test_returns_empty_findings_if_hash_is_wrong(self):
        # filler contains random data, it is necessary to call filter_log() function
        filler = eth_abi.encode_abi(["address"], [AAVE_GOVERNANCE_V2_MAINNET])
        tx_event = create_transaction_event({
            'receipt': {
                'logs': [
                    {'topics': ["0x1010101010101010101010101010101010101010"],
                     'data': filler,
                     'address': AAVE_GOVERNANCE_V2_MAINNET}, ]},

        })
        findings = handle_transaction(tx_event)
        assert len(findings) == 0

    def test_returns_findings_if_everything_is_correct(self):
        # filler contains random data, it is necessary to call filter_log() function
        filler = eth_abi.encode_abi(["address"], [AAVE_GOVERNANCE_V2_MAINNET])
        topics = [event_abi_to_log_topic(json.loads(GOVERNANCE_PROPOSAL_EXECUTED_ABI)), filler]
        tx_event = create_transaction_event({
            'receipt': {
                'logs': [
                    {'topics': topics,
                     'data': filler,
                     'address': AAVE_GOVERNANCE_V2_MAINNET}, ]},

        })
        findings = handle_transaction(tx_event)
        assert len(findings) != 0


TestAaveGovernanceAgent().test_returns_findings_if_everything_is_correct()