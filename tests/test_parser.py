import pytest
from extractor import parser

def test_extract_contacts_basic():
    """Test basic contact extraction from table, contact line, and mailto link."""
    html = """
    <html>
        <body>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                </tr>
                <tr>
                    <td>Alice Johnson</td>
                    <td>alice@example.com</td>
                    <td>555-1234</td>
                </tr>
            </table>
            <p>Contact: Bob Singh</p>
            <p>Email: bob.singh@example.org</p>
            <a href="mailto:charlie@sample.io">Charlie Brown</a>
        </body>
    </html>
    """
    
    result = parser.extract_contacts(html, source_url='test')
    
    # Extract all emails from results
    extracted_emails = [contact.get('email') for contact in result if contact.get('email')]
    
    # Assert expected emails are present
    assert 'alice@example.com' in extracted_emails
    assert 'bob.singh@example.org' in extracted_emails
    assert 'charlie@sample.io' in extracted_emails