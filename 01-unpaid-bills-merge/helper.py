def wrap_link(netsuite_account_id, remote_id):
    return f"<a href='https://td{netsuite_account_id}.app.netsuite.com/app/accounting/transactions/vendbill.nl?id={remote_id}&whence='>{remote_id}</a>"
