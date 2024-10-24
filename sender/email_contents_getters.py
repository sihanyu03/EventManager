from email_content import EmailContent

from typing import Any


def default_getter(data: list[tuple[Any, ...]], cols: list[str], body: str):
    """
    Default email contents list builder. Takes only first_name, and personalises that to the email template
    :param data: Data from SQL table
    :param cols: Columns of the SQL data
    :param body: Email template on which the personalised email will be built on
    :return: List of the EmailContent objects
    """
    email_contents = []

    for row in data:
        values = {cols[i]: row[i] for i in range(len(cols))}

        curr_body = body.format(**values)

        email_contents.append(EmailContent(
            email=values['email'],
            body=curr_body
        ))

    return email_contents


def families(data: list[tuple[Any, ...]], _, body: str) -> list[EmailContent]:
    """
    EmailContent list builder for ISC Families emails
    :param data: Data from SQL table
    :param body: Email template on which the personalised email will be built on
    :return: List of the EmailContent objects
    """
    def generate_table(lst: list[tuple[Any, ...]], tag_start: str = '', tag_end: str = '') -> str:
        """
        Generates the table for the email, reused to create both parents' and children's part
        :param lst: List of the members to build the table on
        :param tag_start: html tag, namely <b> or an empty string. Used to bold parents' table
        :param tag_end: html tag, namely </b> or an empty string. Used to bold parents' table
        :return:
        """
        table = []
        for member in lst:
            first_name, last_name, email, subject, college = member
            table.append(f'''<tr>
                <td>{tag_start}{first_name} {last_name}{tag_end}</td>
                <td>{tag_start}{email}{tag_end}</td>
                <td>{tag_start}{subject}{tag_end}</td>
                <td>{tag_start}{college}{tag_end}</td>
            </tr>''')

        return ''.join(table)

    def add_to_email_contents(lst: list[str], body: str) -> None:
        """
        Adds to the list email_contents
        :param lst: List of members to add, either the parents or the children
        :param body: Almost personalised email. Only missing the name part in 'Dear {receiver}'
        :return: None. Modifies 'email_contents' in-place
        """
        for member in lst:
            first_name = member[0]
            email = member[2]
            email_contents.append(EmailContent(
                email=email,
                body=body.format(receiver=first_name)
            ))

    families = {}

    for row in data:
        family_id, first_name, last_name, email, subject, college, member = row

        if family_id not in families:
            families[family_id] = {'parent': [], 'child': []}

        families[family_id][member].append((
            first_name,
            last_name,
            email,
            subject,
            college
        ))

    email_contents = []
    for family_id in families:
        parents_table = generate_table(families[family_id]['parent'], '<b>', '</b>')
        children_table = generate_table(families[family_id]['child'])

        curr_body = body.format(
            receiver='{receiver}',
            parents_table=parents_table,
            children_table=children_table
        )

        add_to_email_contents(families[family_id]['parent'], curr_body)
        add_to_email_contents(families[family_id]['child'], curr_body)

    return email_contents


def culs_mentorship_scheme(data: list[tuple[Any, ...]], _, body: str) -> list[EmailContent]:
    """
    EmailContent list builder for CULS mentorship scheme emails
    :param data: Data from SQL table
    :param body: Email template on which the personalised email will be built on
    :return: List of the EmailContent objects
    """

    def generate_table(lst: list[tuple[Any, ...]], tag_start: str = '', tag_end: str = '') -> str:
        """
        Generates the table for the email, reused to create both mentor's and mentees' part
        :param lst: List of the members to build the table on
        :param tag_start: html tag, namely <b> or an empty string. Used to bold mentor's table
        :param tag_end: html tag, namely </b> or an empty string. Used to bold mentees' table
        :return:
        """
        table = []
        for member in lst:
            first_name, last_name, email = member
            table.append(f'''<tr>
                <td>{tag_start}{first_name} {last_name}{tag_end}</td>
                <td>{tag_start}{email}{tag_end}</td>
            </tr>''')

        return ''.join(table)

    def add_to_email_contents(lst: list[str], body: str, role: str) -> None:
        """
        Adds to the list email_contents
        :param lst: List of members to add, either the mentor or the mentees
        :param body: Almost personalised email. Only missing the name part in 'Dear {receiver}', and the opposite role
        :param role: The role of the members, either 'mentor' or 'mentee'
        :return: None. Modifies 'email_contents' in-place
        """
        for member in lst:
            first_name = member[0]
            email = member[2]
            opposite_role = 'mentor' if role == 'mentee' else 'mentees'
            is_are = 'is' if role == 'mentee' else 'are'
            email_contents.append(EmailContent(
                email=email,
                body=body.format(
                    receiver=first_name,
                    opposite_role=opposite_role,
                    is_are=is_are
                )
            ))

    groups = {}

    for row in data:
        group_id, first_name, last_name, email, role = row

        if group_id not in groups:
            groups[group_id] = {'mentor': [], 'mentee': []}

        groups[group_id][role].append((
            first_name,
            last_name,
            email
        ))

    email_contents = []
    for group_id in groups:
        mentor_table = generate_table(groups[group_id]['mentor'], '<b>', '</b>')
        mentee_table = generate_table(groups[group_id]['mentee'])

        curr_body = body.format(
            receiver='{receiver}',
            opposite_role='{opposite_role}',
            is_are='{is_are}',
            mentor_table=mentor_table,
            mentee_table=mentee_table
        )

        add_to_email_contents(groups[group_id]['mentor'], curr_body, 'mentor')
        add_to_email_contents(groups[group_id]['mentee'], curr_body, 'mentee')

    return email_contents
