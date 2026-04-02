from epstein_files.documents.config.config_builder import phone_bill_cfg


PHONE_BILL_CFGS = [
    phone_bill_cfg('EFTA00007070', 'MetroPCS', '2006'),
    phone_bill_cfg('EFTA00006770', 'MetroPCS', '2006-02-01 to 2006-06-16'),
    phone_bill_cfg('EFTA00006870', 'MetroPCS', '2006-02-09 to 2006-07'),
    phone_bill_cfg('EFTA00006970', 'MetroPCS', '2006-04-15 to 2006-07-16'),
    phone_bill_cfg('EFTA00007401', 'T-Mobile', '2004-08-25 to 2005-07-13'),
    phone_bill_cfg('EFTA00007501', 'T-Mobile', '2005'),
    phone_bill_cfg('EFTA00006487', 'T-Mobile', '2006'),
    phone_bill_cfg('EFTA00006387', 'T-Mobile', '2006-06-15 to 2006-07-23'),
    phone_bill_cfg('EFTA00006587', 'T-Mobile', '2006-09-04 to 2016-10-15'),
    phone_bill_cfg('EFTA00006687', 'T-Mobile', '2006-10-31 to 2006-12-25'),
    # These two are subpoena response letters w/attached phone bill)
    phone_bill_cfg('EFTA00007301', 'T-Mobile', 'Blackberry phone logs for 2005', date='2007-03-23'),
    phone_bill_cfg('EFTA00007253', 'T-Mobile', date='2007-03-23'),
    phone_bill_cfg('EFTA01310850', 'AT&T', date='2004-10-11'),
    phone_bill_cfg('EFTA00203152', 'Cingular Wireless', date='2005-07-15'),
]
