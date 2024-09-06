emails = {
    'event_test': {
        'name': 'Event test',
        'table_name': 'test',
        'subject': 'Test email',
        'attachment': 'ISC_logo.png',
        'text': '''
        <!DOCTYPE html>
        <html>
            <body>
                <p>Dear {first_name},</p>
                <p>Thank you for signing up to this event. The location is <b><u>Christ's College</u></b> and time is 
                <b><u>Monday 2nd of September</u></b>.</p>
                <p>Please be there on time.</p>
                <p></p>
                <p>Best Regards,</p>
                <p>ISC Committee 2024-25</p>
                <img src="cid:image" width="150">
            </body>
        </html>
        '''
    },
    '': {
        'name': 'MCR International Officers WhatsApp Invitation',
        'table_name': 'mcr_intl_officers_wa_invitation',
        'subject': "Invitation to MCR International Officers' WhatsApp Group",
        'attachment': None,
        'text': '''
        <!DOCTYPE html>
        <html>
            <body>
                <p>Dear {first_name},</p>
                <p></p>
                <p>This is Hailey, the International Students Campaign college coordinator this year. As the college 
                coordinator, I’m hoping that internationals can get to know each other better, so it would be great if 
                you can help us with promoting our events and activities. Similarly, I’ll be more than happy to support 
                you and your college if you would like to reach out to ISC for anything!</p>
                <p></p>
                <p>I’ll be making a Whatsapp group with all the MCR international officers and the ISC executive
                 committee. Could you please join with this link: https://chat.whatsapp.com/ClMloH5eLkvIPNE2vZSTcM</p>
                <p>Let me know if you have any questions. Thanks!</p>
                <p></p>
                <p>Best regards,</p>
                <p>Hailey</p>
            </body>
        </html>
        '''
    }
}
