from twilio.rest import Client
from core.interfaces import Writer
from core.data_wrapper import DataWrapper

class TwilioWriter(Writer):
    """
    Writer for sending SMS via Twilio.
    """

    def __init__(self, account_sid: str, auth_token: str, from_number: str, service_name="twilio_cred"):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.service_name = service_name
        self.client = None

    def initialize(self):
        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, data: DataWrapper, to_number: str, message: str):
        """
        Send an SMS message to a recipient.

        Args:
            data (DataWrapper): Not used, included for interface compatibility.
            to_number (str): The recipient's phone number.
            message (str): The message text.
        """
        self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=to_number
        )
        print(f"[TwilioWriter] SMS sent to {to_number}")

    def get_operations(self):
        return {
            "send_sms": self.send_sms
        }
