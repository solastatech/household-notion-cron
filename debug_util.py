from debug_config import verbose
from send_test_noti import send_bark_notification

def debug(*args):
    """Print debug messages only when verbose is True."""
    if verbose == True:
        print(*args)

def debug_df(df):
    """Print debug messages for dataframes only when verbose is True."""
    if verbose == True:
        df.info()

def debug_noti():
    """Test ping only when verbose is True."""
    if verbose == True:
        send_bark_notification("Test", "Ping")