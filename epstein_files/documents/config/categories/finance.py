"""
Finance related documents not specifically about Epstein's money.
"""
from epstein_files.documents.config.config_builder import press_release
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.documents.categories import Interesting, Neutral
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *

DEUTSCHE_BANK_TAX_TOPICS = f'{DEUTSCHE_BANK} Wealth Management Tax Topics'
JP_MORGAN_EYE_ON_THE_MARKET = f"Eye On The Market"
UBS_CIO_REPORT = 'CIO Monthly Extended report'


# All authors of documents in this category will be marked uninteresting
FINANCE_CFGS = [
    DocCfg(id='024631', author='Ackrell Capital', note=f"Cannabis Investment Report 2018", is_interesting=True),
    DocCfg(id='016111', author=BOFA_MERRILL, note=f"GEMs Paper #26 Saudi Arabia: beyond oil but not so fast", date='2016-06-30'),
    DocCfg(id='010609', author=BOFA_MERRILL, note=f"Liquid Insight Trump's effect on MXN", date='2016-09-22'),
    DocCfg(id='025978', author=BOFA_MERRILL, note=f"Understanding when risk parity risk Increases", date='2016-08-09'),
    DocCfg(id='014404', author=BOFA_MERRILL, note=f'Japan Investment Strategy Report', date='2016-11-18'),
    DocCfg(id='014410', author=BOFA_MERRILL, note=f'Japan Investment Strategy Report', date='2016-11-18'),
    DocCfg(id='014424', author=BOFA_MERRILL, note=f"Japan Macro Watch", date='2016-11-14'),
    DocCfg(id='014731', author=BOFA_MERRILL, note=f"Global Rates, FX & EM 2017 Year Ahead", date='2016-11-16'),
    DocCfg(id='014432', author=BOFA_MERRILL, note=f"Global Cross Asset Strategy - Year Ahead The Trump inflection", date='2016-11-30'),
    DocCfg(id='014460', author=BOFA_MERRILL, note=f"European Equity Strategy 2017", date='2016-12-01'),
    DocCfg(id='014972', author=BOFA_MERRILL, note=f"Global Equity Volatility Insights", date='2017-06-20'),
    DocCfg(id='014622', author=BOFA_MERRILL, note=f"Top 10 US Ideas Quarterly", date='2017-01-03'),
    DocCfg(id='023069', author=BOFA_MERRILL, note=f"Equity Strategy Focus Point Death and Taxes", date='2017-01-29'),
    DocCfg(id='014721', author=BOFA_MERRILL, note=f"Cause and Effect Fade the Trump Risk Premium", date='2017-02-13'),
    DocCfg(id='014887', author=BOFA_MERRILL, note=f"Internet / e-Commerce", date='2017-04-06'),
    DocCfg(id='014873', author=BOFA_MERRILL, note=f"Hess Corp", date='2017-04-11'),
    DocCfg(id='023575', author=BOFA_MERRILL, note=f"Global Equity Volatility Insights", date='2017-06-01'),
    DocCfg(id='014518', author=BOFA_WEALTH_MGMT, note=f'tax alert', date='2016-05-02'),
    DocCfg(id='029438', author=BOFA_WEALTH_MGMT, note=f'tax report', date='2018-01-02'),
    DocCfg(id='026668', author="Boothbay Fund Management", note=f"2016-Q4 earnings report signed by Ari Glass", is_interesting=True),
    DocCfg(id='024302', author='Carvana', note=f"form 14A SEC filing proxy statement", date='2019-04-23'),
    DocCfg(id='029305', author='CCH Tax', note=f"Briefing on end of Defense of Marriage Act", date='2013-06-27'),
    DocCfg(id='026794', author=DEUTSCHE_BANK, note=f"Global Political and Regulatory Risk in 2015/2016"),
    DocCfg(id='022361', author=DEUTSCHE_BANK_TAX_TOPICS, date='2013-05-01', attached_to_email_id='022359'),
    DocCfg(id='022325', author=DEUTSCHE_BANK_TAX_TOPICS, date='2013-12-20'),
    DocCfg(id='022330', author=DEUTSCHE_BANK_TAX_TOPICS, date='2013-12-20', note='table of contents'),
    DocCfg(id='019440', author=DEUTSCHE_BANK_TAX_TOPICS, date='2014-01-29'),
    DocCfg(id='024202', author=ELECTRON_CAPITAL_PARTNERS, note=f"Global Utility White Paper", date='2013-03-08'),
    DocCfg(id='022372', author='Ernst & Young', date='2016-11-09', note=f'2016 election report'),
    DocCfg(id='014532', author=GOLDMAN_INVESTMENT_MGMT, note=f"Outlook - Half Full", date='2017-01-01'),
    DocCfg(
        id='026909',
        attached_to_email_id='026893',
        author=GOLDMAN_INVESTMENT_MGMT,
        note=f"The Unsteady Undertow Commands the Seas (Temporarily)",
        date='2018-10-14',
    ),
    DocCfg(id='026944', author=GOLDMAN_INVESTMENT_MGMT, note=f"Risk of a US-Iran Military Conflict", date='2019-05-23'),
    DocCfg(id='018804', author='Integra Realty Resources', note=f"appraisal of going concern for IGY American Yacht Harbor Marina in {VIRGIN_ISLANDS}"),
    DocCfg(id='026679', author='Invesco', note=f"Global Sovereign Asset Management Study 2017"),
    DocCfg(
        id='033220',
        author='Joseph G. Carson',
        note=f"short economic report on defense spending under Trump",
        is_interesting=True,
    ),
    DocCfg(id='026572', author=JP_MORGAN, note=f"Global Asset Allocation report", date='2012-11-09'),
    DocCfg(id='030848', author=JP_MORGAN, note=f"Global Asset Allocation report", date='2013-03-28'),
    DocCfg(id='030840', author=JP_MORGAN, note=f"Market Thoughts"),
    DocCfg(id='022350', author=JP_MORGAN, note=f"tax efficiency of Intentionally Defective Grantor Trusts (IDGT)"),
    DocCfg(id='025242', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-04-09'),
    DocCfg(id='030010', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, attached_to_email_id='030006', date='2011-06-14'),
    DocCfg(id='030808', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-07-11'),
    DocCfg(id='025221', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-07-25'),
    DocCfg(id='025229', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-08-04'),
    DocCfg(id='030814', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, date='2011-11-21'),
    DocCfg(id='024132', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-03-15'),
    DocCfg(id='024194', author=JP_MORGAN, note=JP_MORGAN_EYE_ON_THE_MARKET, date='2012-10-22'),
    DocCfg(id='025296', author='Laffer Associates', note=f'report predicting Trump win', date='2016-07-06'),
    DocCfg(
        id='020824',
        author='Mary Meeker',
        date='2011-02-01',
        note=f"USA Inc: A Basic Summary of America's Financial Statements compiled",
    ),
    DocCfg(id='025551', author='Morgan Stanley', note=f'report about alternative asset managers', date='2018-01-30'),
    DocCfg(id='019856', author='Sadis Goldberg LLP', note=f"report on SCOTUS ruling about insider trading", is_interesting=True),
    DocCfg(id='025763', author='S&P', note=f"Economic Research: How Increasing Income Inequality Is Dampening U.S. Growth", date='2014-08-05'),
    DocCfg(id='024135', author=UBS, note=UBS_CIO_REPORT, date='2012-06-29'),
    DocCfg(id='025247', author=UBS, note=UBS_CIO_REPORT, date='2012-10-25'),
    DocCfg(id='026584', note="article about tax implications of disregarded entities", date='2009-07-01', is_interesting=True),
    DocCfg(id='024817', note="Cowen's CBD / Cannabis report", date='2019-02-25', is_interesting=True),
    press_release(
        '012048',
        None,
        note=f"Rockefeller Partners with Gregory J. Fleming to Create Independent Financial Services Firm and other articles",
        is_interesting=False,
    ),

    # DOJ
    DocCfg(id='EFTA00286949', author='Nathaniel August', note='Mangrove Partners valuation report', date='2016-11-03'),
    DocCfg(id='EFTA01078403', author=ATORUS, note='investment adviser uniform application', date='2014-05-14'),
    DocCfg(id='EFTA02690885', author=ATORUS, note='pitch deck'),
    DocCfg(id='EFTA00593276', author=EDMOND_DE_ROTHSCHILD, note='org chart', is_interesting=True),
    # Prop trading / HFT
    DocCfg(id='EFTA00611806', author='Adam Campbell', note='CEA, LLC High Liquidity Trading Program presentation'),
    DocCfg(id='EFTA01088824', author='Boothbay', note='Absolute Return Strategies Fund pitch deck'),
    DocCfg(id='EFTA00556664', author='Qarmin', note='high frequency trading pitch deck'),
]
