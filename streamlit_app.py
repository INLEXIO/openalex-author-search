import streamlit as st
import json
import pandas as pd
from io import BytesIO
from collections import defaultdict, Counter
import unicodedata

# Configure page
st.set_page_config(
    page_title="OpenAlex Author Search",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS to match your branding (customize colors here)
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #164A78;
        color: white;
        font-size: 16px;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0d3050;
    }
    h1 {
        color: #164A78;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# UTILITY FUNCTIONS (from your existing code)
# ============================================================================

def normalize_author_name(name):
    """Normalize author names to handle accents and dashes"""
    if not name:
        return name
    
    normalized = unicodedata.normalize('NFD', name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    
    ascii_name = ascii_name.replace('–', '-')
    ascii_name = ascii_name.replace('—', '-')
    ascii_name = ascii_name.replace('−', '-')
    ascii_name = ascii_name.replace('‐', '-')
    ascii_name = ascii_name.replace('‑', '-')
    
    ascii_name = ' '.join(ascii_name.split())
    
    return ascii_name.strip()

COUNTRY_CODES = {
    'AD': 'Andorra', 'AL': 'Albania', 'AM': 'Armenia', 'AT': 'Austria',
    'AX': 'Åland Islands', 'BA': 'Bosnia and Herzegovina', 'BE': 'Belgium',
    'BG': 'Bulgaria', 'BY': 'Belarus', 'CH': 'Switzerland', 'CY': 'Cyprus',
    'CZ': 'Czech Republic', 'DE': 'Germany', 'DK': 'Denmark', 'EE': 'Estonia',
    'ES': 'Spain', 'FI': 'Finland', 'FO': 'Faroe Islands', 'FR': 'France',
    'GB': 'United Kingdom', 'UK': 'United Kingdom', 'GE': 'Georgia',
    'GG': 'Guernsey', 'GI': 'Gibraltar', 'GR': 'Greece', 'HR': 'Croatia',
    'HU': 'Hungary', 'IE': 'Ireland', 'IM': 'Isle of Man', 'IS': 'Iceland',
    'IT': 'Italy', 'JE': 'Jersey', 'LI': 'Liechtenstein', 'LT': 'Lithuania',
    'LU': 'Luxembourg', 'LV': 'Latvia', 'MC': 'Monaco', 'MD': 'Moldova',
    'ME': 'Montenegro', 'MK': 'North Macedonia', 'MT': 'Malta', 'NL': 'Netherlands',
    'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
    'RS': 'Serbia', 'RU': 'Russia', 'SE': 'Sweden', 'SI': 'Slovenia',
    'SJ': 'Svalbard and Jan Mayen', 'SK': 'Slovakia', 'SM': 'San Marino',
    'UA': 'Ukraine', 'VA': 'Vatican City', 'XK': 'Kosovo',
    'AE': 'United Arab Emirates', 'AF': 'Afghanistan', 'AZ': 'Azerbaijan',
    'BD': 'Bangladesh', 'BH': 'Bahrain', 'BN': 'Brunei', 'BT': 'Bhutan',
    'CN': 'China', 'HK': 'Hong Kong', 'ID': 'Indonesia', 'IL': 'Israel',
    'IN': 'India', 'IQ': 'Iraq', 'IR': 'Iran', 'JO': 'Jordan', 'JP': 'Japan',
    'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KP': 'North Korea', 'KR': 'South Korea',
    'KW': 'Kuwait', 'KZ': 'Kazakhstan', 'LA': 'Laos', 'LB': 'Lebanon',
    'LK': 'Sri Lanka', 'MM': 'Myanmar', 'MN': 'Mongolia', 'MO': 'Macau',
    'MV': 'Maldives', 'MY': 'Malaysia', 'NP': 'Nepal', 'OM': 'Oman',
    'PH': 'Philippines', 'PK': 'Pakistan', 'PS': 'Palestine', 'QA': 'Qatar',
    'SA': 'Saudi Arabia', 'SG': 'Singapore', 'SY': 'Syria', 'TH': 'Thailand',
    'TJ': 'Tajikistan', 'TL': 'Timor-Leste', 'TM': 'Turkmenistan', 'TR': 'Turkey',
    'TW': 'Taiwan', 'UZ': 'Uzbekistan', 'VN': 'Vietnam', 'YE': 'Yemen',
    'AO': 'Angola', 'BF': 'Burkina Faso', 'BI': 'Burundi', 'BJ': 'Benin',
    'BW': 'Botswana', 'CD': 'Democratic Republic of the Congo',
    'CF': 'Central African Republic', 'CG': 'Republic of the Congo',
    'CI': 'Ivory Coast', 'CM': 'Cameroon', 'CV': 'Cape Verde', 'DJ': 'Djibouti',
    'DZ': 'Algeria', 'EG': 'Egypt', 'EH': 'Western Sahara', 'ER': 'Eritrea',
    'ET': 'Ethiopia', 'GA': 'Gabon', 'GH': 'Ghana', 'GM': 'Gambia',
    'GN': 'Guinea', 'GQ': 'Equatorial Guinea', 'GW': 'Guinea-Bissau',
    'KE': 'Kenya', 'KM': 'Comoros', 'LR': 'Liberia', 'LS': 'Lesotho',
    'LY': 'Libya', 'MA': 'Morocco', 'MG': 'Madagascar', 'ML': 'Mali',
    'MR': 'Mauritania', 'MU': 'Mauritius', 'MW': 'Malawi', 'MZ': 'Mozambique',
    'NA': 'Namibia', 'NE': 'Niger', 'NG': 'Nigeria', 'RE': 'Réunion',
    'RW': 'Rwanda', 'SC': 'Seychelles', 'SD': 'Sudan', 'SL': 'Sierra Leone',
    'SN': 'Senegal', 'SO': 'Somalia', 'SS': 'South Sudan',
    'ST': 'São Tomé and Príncipe', 'SZ': 'Eswatini', 'TD': 'Chad', 'TG': 'Togo',
    'TN': 'Tunisia', 'TZ': 'Tanzania', 'UG': 'Uganda', 'YT': 'Mayotte',
    'ZA': 'South Africa', 'ZM': 'Zambia', 'ZW': 'Zimbabwe',
    'AG': 'Antigua and Barbuda', 'AI': 'Anguilla', 'AW': 'Aruba',
    'BB': 'Barbados', 'BL': 'Saint Barthélemy', 'BM': 'Bermuda',
    'BQ': 'Caribbean Netherlands', 'BS': 'Bahamas', 'BZ': 'Belize',
    'CA': 'Canada', 'CR': 'Costa Rica', 'CU': 'Cuba', 'CW': 'Curaçao',
    'DM': 'Dominica', 'DO': 'Dominican Republic', 'GD': 'Grenada',
    'GL': 'Greenland', 'GP': 'Guadeloupe', 'GT': 'Guatemala', 'HN': 'Honduras',
    'HT': 'Haiti', 'JM': 'Jamaica', 'KN': 'Saint Kitts and Nevis',
    'KY': 'Cayman Islands', 'LC': 'Saint Lucia', 'MF': 'Saint Martin',
    'MQ': 'Martinique', 'MS': 'Montserrat', 'MX': 'Mexico', 'NI': 'Nicaragua',
    'PA': 'Panama', 'PM': 'Saint Pierre and Miquelon', 'PR': 'Puerto Rico',
    'SV': 'El Salvador', 'SX': 'Sint Maarten', 'TC': 'Turks and Caicos Islands',
    'TT': 'Trinidad and Tobago', 'US': 'United States',
    'VC': 'Saint Vincent and the Grenadines', 'VG': 'British Virgin Islands',
    'VI': 'U.S. Virgin Islands',
    'AR': 'Argentina', 'BO': 'Bolivia', 'BR': 'Brazil', 'CL': 'Chile',
    'CO': 'Colombia', 'EC': 'Ecuador', 'FK': 'Falkland Islands',
    'GF': 'French Guiana', 'GY': 'Guyana', 'PE': 'Peru', 'PY': 'Paraguay',
    'SR': 'Suriname', 'UY': 'Uruguay', 'VE': 'Venezuela',
    'AS': 'American Samoa', 'AU': 'Australia', 'CK': 'Cook Islands',
    'FJ': 'Fiji', 'FM': 'Micronesia', 'GU': 'Guam', 'KI': 'Kiribati',
    'MH': 'Marshall Islands', 'MP': 'Northern Mariana Islands',
    'NC': 'New Caledonia', 'NF': 'Norfolk Island', 'NR': 'Nauru', 'NU': 'Niue',
    'NZ': 'New Zealand', 'PF': 'French Polynesia', 'PG': 'Papua New Guinea',
    'PN': 'Pitcairn Islands', 'PW': 'Palau', 'SB': 'Solomon Islands',
    'TK': 'Tokelau', 'TO': 'Tonga', 'TV': 'Tuvalu',
    'UM': 'U.S. Minor Outlying Islands', 'VU': 'Vanuatu',
    'WF': 'Wallis and Futuna', 'WS': 'Samoa'
}

CONTINENT_MAP = {
    'Europe': ['AD', 'AL', 'AT', 'AX', 'BA', 'BE', 'BG', 'BY', 'CH', 'CY',
               'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FO', 'FR', 'GB', 'UK',
               'GG', 'GI', 'GR', 'HR', 'HU', 'IE', 'IM', 'IS', 'IT', 'JE',
               'LI', 'LT', 'LU', 'LV', 'MC', 'MD', 'ME', 'MK', 'MT', 'NL',
               'NO', 'PL', 'PT', 'RO', 'RS', 'SE', 'SI', 'SJ', 'SK', 'SM',
               'UA', 'VA', 'XK'],
    'Asia': ['AE', 'AF', 'AM', 'AZ', 'BD', 'BH', 'BN', 'BT', 'CN', 'GE',
             'HK', 'ID', 'IL', 'IN', 'IQ', 'IR', 'JO', 'JP', 'KG', 'KH',
             'KP', 'KR', 'KW', 'KZ', 'LA', 'LB', 'LK', 'MM', 'MN', 'MO',
             'MV', 'MY', 'NP', 'OM', 'PH', 'PK', 'PS', 'QA', 'SA', 'SG',
             'SY', 'TH', 'TJ', 'TL', 'TM', 'TR', 'TW', 'UZ', 'VN', 'YE'],
    'Africa': ['AO', 'BF', 'BI', 'BJ', 'BW', 'CD', 'CF', 'CG', 'CI', 'CM',
               'CV', 'DJ', 'DZ', 'EG', 'EH', 'ER', 'ET', 'GA', 'GH', 'GM',
               'GN', 'GQ', 'GW', 'KE', 'KM', 'LR', 'LS', 'LY', 'MA', 'MG',
               'ML', 'MR', 'MU', 'MW', 'MZ', 'NA', 'NE', 'NG', 'RE', 'RW',
               'SC', 'SD', 'SL', 'SN', 'SO', 'SS', 'ST', 'SZ', 'TD', 'TG',
               'TN', 'TZ', 'UG', 'YT', 'ZA', 'ZM', 'ZW'],
    'North America': ['AG', 'AI', 'AW', 'BB', 'BL', 'BM', 'BQ', 'BS', 'BZ',
                      'CA', 'CR', 'CU', 'CW', 'DM', 'DO', 'GD', 'GL', 'GP',
                      'GT', 'HN', 'HT', 'JM', 'KN', 'KY', 'LC', 'MF', 'MQ',
                      'MS', 'MX', 'NI', 'PA', 'PM', 'PR', 'SV', 'SX', 'TC',
                      'TT', 'US', 'VC', 'VG', 'VI'],
    'South America': ['AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'FK', 'GF', 'GY',
                      'PE', 'PY', 'SR', 'UY', 'VE'],
    'Oceania': ['AS', 'AU', 'CK', 'FJ', 'FM', 'GU', 'KI', 'MH', 'MP', 'NC',
                'NF', 'NR', 'NU', 'NZ', 'PF', 'PG', 'PN', 'PW', 'SB', 'TK',
                'TO', 'TV', 'UM', 'VU', 'WF', 'WS']
}

def get_country_name(code):
    return COUNTRY_CODES.get(code.upper(), code)

def get_continent(country_code):
    cc = country_code.upper()
    for continent, codes in CONTINENT_MAP.items():
        if cc in codes:
            return continent
    return 'Unknown'

def process_works_to_author_profiles(works, topic_filter=None, journal_filter=None, country_filter=None):
    """Process works into author profiles with filtering"""
    author_profiles = defaultdict(lambda: {
        'count': 0,
        'citations': [],
        'topics': Counter(),
        'coauthors': Counter(),
        'journals': Counter(),
        'countries': Counter(),
        'orcid': '',
        'openalex_id': '',
        'display_name': ''
    })
    
    for work in works:
        citations = work.get('cited_by_count', 0)
        
        primary_loc = work.get('primary_location', {})
        source = primary_loc.get('source', {}) if primary_loc else {}
        journal = source.get('display_name', 'Unknown')
        
        topic = work.get('primary_topic')
        topic_name = topic.get('display_name', 'Unknown') if topic else 'Unknown'
        
        # Apply filters
        if topic_filter and topic_filter not in topic_name.lower():
            continue
        
        if journal_filter and journal_filter not in journal.lower():
            continue
        
        if country_filter:
            work_has_country = False
            for authorship in work.get('authorships', []):
                countries = authorship.get('countries', [])
                for country_code in countries:
                    if country_code:
                        country_name = get_country_name(country_code).lower()
                        if country_filter in country_name or country_filter in country_code.lower():
                            work_has_country = True
                            break
                if work_has_country:
                    break
            if not work_has_country:
                continue
        
        # Process authors
        for authorship in work.get('authorships', []):
            author_info = authorship.get('author', {})
            author_name = author_info.get('display_name', 'Unknown')
            
            if not author_name or author_name == 'Unknown':
                continue
            
            normalized_name = normalize_author_name(author_name)
            profile = author_profiles[normalized_name]
            
            if not profile['display_name']:
                profile['display_name'] = author_name
            
            profile['count'] += 1
            profile['citations'].append(citations)
            
            if author_info.get('orcid') and not profile['orcid']:
                profile['orcid'] = author_info['orcid']
            if author_info.get('id') and not profile['openalex_id']:
                profile['openalex_id'] = author_info['id']
            
            if topic_name != 'Unknown':
                profile['topics'][topic_name] += 1
            
            for other_auth in work.get('authorships', []):
                other_name = other_auth.get('author', {}).get('display_name', '')
                if other_name and other_name != author_name:
                    profile['coauthors'][other_name] += 1
            
            if journal != 'Unknown':
                profile['journals'][journal] += 1
            
            countries = authorship.get('countries', [])
            for country_code in countries:
                if country_code:
                    profile['countries'][country_code] += 1
    
    return author_profiles

# ============================================================================
# STREAMLIT UI
# ============================================================================

st.title("🔍 OpenAlex Author Search")
st.markdown("Search and analyze author data from your OpenAlex export")

# Sidebar for instructions
with st.sidebar:
    st.header("📖 How to Use")
    st.markdown("""
    1. **Export data from Excel**: 
       - In Excel, run your data fetch
       - Save the Data sheet as JSON
    
    2. **Upload the JSON file** here
    
    3. **Enter search criteria** (all optional)
    
    4. **Click Search** to see results
    
    5. **Download Excel** file with results
    """)
    
    st.markdown("---")
    st.markdown("**Need help?**  \nContact: your@email.com")

# File upload
uploaded_file = st.file_uploader(
    "Upload your OpenAlex data (JSON format)",
    type=['json'],
    help="Export your works data from Excel as JSON first"
)

if uploaded_file:
    try:
        # Load data
        works = json.load(uploaded_file)
        st.success(f"✅ Loaded {len(works):,} works from file")
        
        # Search criteria in columns
        col1, col2 = st.columns(2)
        
        with col1:
            topic_search = st.text_input(
                "🔬 Search by Topic",
                placeholder="e.g., neuroscience",
                help="Filter works by topic keyword (case-insensitive)"
            )
            
            author_search = st.text_input(
                "👤 Search by Author Name",
                placeholder="e.g., Smith",
                help="Filter authors by name (partial match)"
            )
        
        with col2:
            journal_search = st.text_input(
                "📄 Search by Journal",
                placeholder="e.g., Nature",
                help="Filter works by journal name"
            )
            
            country_search = st.text_input(
                "🌍 Search by Country",
                placeholder="e.g., United States or US",
                help="Filter authors by country (name or code)"
            )
        
        # Additional options
        col3, col4, col5 = st.columns(3)
        
        with col3:
            min_articles = st.number_input(
                "Minimum Articles",
                min_value=1,
                max_value=100,
                value=3,
                help="Minimum number of publications"
            )
        
        with col4:
            max_results = st.number_input(
                "Maximum Results",
                min_value=1,
                max_value=500,
                value=50,
                help="Maximum number of authors to display"
            )
        
        with col5:
            sort_by = st.selectbox(
                "Sort By",
                ["Count", "Average Citations", "Median Citations", "Score"],
                help="How to sort the results"
            )
        
        # Search button
        if st.button("🔍 Search Authors", type="primary"):
            with st.spinner("Processing author profiles..."):
                
                # Process works
                profiles = process_works_to_author_profiles(
                    works,
                    topic_filter=topic_search.lower() if topic_search else None,
                    journal_filter=journal_search.lower() if journal_search else None,
                    country_filter=country_search.lower() if country_search else None
                )
                
                # Build results
                results = []
                for normalized_name, profile in profiles.items():
                    if profile['count'] < min_articles:
                        continue
                    
                    # Author name filter
                    if author_search:
                        display_name = profile['display_name'].lower()
                        if author_search.lower() not in normalized_name.lower() and author_search.lower() not in display_name:
                            continue
                    
                    citations = profile['citations']
                    median_cites = sorted(citations)[len(citations)//2] if citations else 0
                    avg_cites = round(sum(citations) / len(citations), 1) if citations else 0
                    
                    most_common_country = profile['countries'].most_common(1)
                    country_code = most_common_country[0][0] if most_common_country else ''
                    country_name = get_country_name(country_code)
                    continent = get_continent(country_code)
                    
                    top_topics = ', '.join([t for t, _ in profile['topics'].most_common(5)])
                    top_coauthors = ', '.join([c for c, _ in profile['coauthors'].most_common(5)])
                    top_journals = ', '.join([j for j, _ in profile['journals'].most_common(5)])
                    
                    # Calculate score
                    score = 0
                    if profile['count'] >= 10:
                        score += 1
                    if median_cites >= 5:
                        score += 1
                    if profile['orcid']:
                        score += 1
                    
                    results.append({
                        'Author': profile['display_name'],
                        'Count': profile['count'],
                        'Median Citations': median_cites,
                        'Average Citations': avg_cites,
                        'Country': country_name,
                        'Continent': continent,
                        'Top Topics': top_topics,
                        'Top Co-authors': top_coauthors,
                        'Top Journals': top_journals,
                        'ORCID': profile['orcid'] if profile['orcid'] else '',
                        'OpenAlex ID': profile['openalex_id'] if profile['openalex_id'] else '',
                        'Score': score
                    })
                
                # Sort results
                if sort_by == "Count":
                    results.sort(key=lambda x: x['Count'], reverse=True)
                elif sort_by == "Average Citations":
                    results.sort(key=lambda x: x['Average Citations'], reverse=True)
                elif sort_by == "Median Citations":
                    results.sort(key=lambda x: x['Median Citations'], reverse=True)
                elif sort_by == "Score":
                    results.sort(key=lambda x: (x['Score'], x['Count']), reverse=True)
                
                # Limit results
                results = results[:max_results]
                
                if results:
                    st.success(f"✅ Found {len(results)} matching authors")
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(results)
                    
                    # Display results
                    st.dataframe(
                        df,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Summary statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Authors", len(results))
                    with col2:
                        st.metric("Avg Publications", f"{df['Count'].mean():.1f}")
                    with col3:
                        st.metric("Avg Citations", f"{df['Average Citations'].mean():.1f}")
                    with col4:
                        st.metric("With ORCID", df['ORCID'].astype(bool).sum())
                    
                    # Download button
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Author Search Results')
                    
                    st.download_button(
                        label="📥 Download Results (Excel)",
                        data=output.getvalue(),
                        file_name="author_search_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                else:
                    st.warning("No authors match your search criteria. Try adjusting your filters.")
    
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON file. Please upload a valid JSON export from Excel.")
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
else:
    st.info("👆 Upload your OpenAlex data JSON file to get started")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>OpenAlex Author Search Tool | Powered by Streamlit</small>
</div>
""", unsafe_allow_html=True)
```

### **File 2: `requirements.txt`**
```
streamlit==1.29.0
pandas==2.1.4
openpyxl==3.1.2