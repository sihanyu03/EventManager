from email_sender import EmailSender
from recipient import Recipient
import json


class FamiliesEmailSender(EmailSender):
    def fill_recipients(self, event_key: str):
        """
        :param event_key: The identifier of the event, the key in the 'events' dictionary
        :return:
        """
        for row in self.rows:
            first_name = row[0]
            last_name = row[1]
            email = row[2]
            subject = row[3]
            college = row[4]
            social_media = row[5]
            partner_first_name = row[6]
            partner_last_name = row[7]
            partner_email = row[8]
            partner_subject = row[9]
            partner_college = row[10]
            partner_social_media = row[11]
            children = json.loads(row[12])

            children_table = []
            for child_name, vals in children.items():
                child_email = vals[0]
                child_subject = vals[1]
                child_college = vals[2]
                child_social_media = vals[3]
                children_table.append(
                    f'''<tr>
                        <td>{child_email}</td>
                        <td>{child_name}</td>
                        <td>{child_subject}</td>
                        <td>{child_college}</td>
                        <td>{child_social_media}</td>
                    <!tr>
                    ''')

            text = emails[event_key]['text'].format(
                receiver='{receiver}',
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                college=college,
                social_media=social_media,
                partner_first_name=partner_first_name,
                partner_last_name=partner_last_name,
                partner_email=partner_email,
                partner_subject=partner_subject,
                partner_college=partner_college,
                partner_social_media=partner_social_media,
                children_table=''.join(children_table)
            )

            self.recipients.append(Recipient(
                email=email,
                text=text.format(receiver=first_name)
            ))

            self.recipients.append(Recipient(
                email=partner_email,
                text=text.format(receiver=partner_first_name)
            ))

            for name, vals in children.items():
                child_first_name = name.split()[0]
                child_email = vals[0]
                self.recipients.append(Recipient(
                    email=child_email,
                    text=text.format(receiver=child_first_name)
                ))

        self.length = len(self.recipients)
