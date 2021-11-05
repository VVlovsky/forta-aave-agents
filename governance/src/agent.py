import forta_agent
from forta_agent import Finding, FindingType, FindingSeverity
from src.constants import AAVE_GOVERNANCE_V2_MAINNET, GOVERNANCE_PROPOSAL_EXECUTED_ABI


def handle_transaction(transaction_event: forta_agent.transaction_event.TransactionEvent):
    findings = []

    # filter transaction events where GOVERNANCE_PROPOSAL_EXECUTED event is in the log with AAVE_GOVERNANCE_V2 address
    events = transaction_event.filter_log(GOVERNANCE_PROPOSAL_EXECUTED_ABI,
                                          AAVE_GOVERNANCE_V2_MAINNET)
    for event in events:
        id = event.get('args', {}).get('id', None)  # attempt to get proposal id
        id = id if id else 'UNKNOWN ID'  # set 'UNKNOWN ID' if failed
        initiator_execution = event.get('args', {}).get('initiatorExecution', None)  # attempt to get initiator
        initiator_execution = initiator_execution if initiator_execution else 'UNKNOWN INITIATOR'
        # set 'UNKNOWN INITIATOR' if failed

        findings.append(Finding({
            'name': 'Aave Governance Proposal is EXECUTED',
            'description': f'Aave governance proposal with id {id} is executed by {initiator_execution}',
            'alert_id': 'AAVE-GOV-EXEC',
            'type': FindingType.Info,
            'severity': FindingSeverity.Info,
            'metadata': {
                'id': id,
                'initiator_execution': initiator_execution
            }
        }))

    return findings
