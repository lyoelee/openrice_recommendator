import requests, json, math, logging, scrapy, re, pandas as pd

# fake to become a browser
headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }

# grab the entire list of restuarants for HK on openrice, only focusing on the review links
review_url     = []
category_id    = []
category_name  = []
name           = []
district       = []
district_id    = []
price_UI       = []
address        = []
latitude       = []
longitude      = []
review_count   = []
score_smile    = []
score_cry      = []
bookmark_count = []
score_overall  = []

for i in range(1,20):
    
    r = requests.get("https://www.openrice.com/api/pois?uiLang=en&uiCity=hongkong&page="+ str(i) +"&&sortBy=Default&districtId=2008", headers = headers)
    result = json.loads(r.text)
    
    if len(result['searchResult']['paginationResult']['results']) == 0:
        break

    for j in range(len(result['searchResult']['paginationResult']['results'])):
        review_url.append(result['searchResult']['paginationResult']['results'][j]['reviewUrlUI'])
        name.append(result['searchResult']['paginationResult']['results'][j]['nameUI'].encode('utf-8'))
        district.append(result['searchResult']['paginationResult']['results'][j]['district']['name'])
        district_id.append(result['searchResult']['paginationResult']['results'][j]['district']['districtId'])
        address.append(result['searchResult']['paginationResult']['results'][j]['address'])
        price_UI.append(result['searchResult']['paginationResult']['results'][j]['priceUI'])
        latitude.append(result['searchResult']['paginationResult']['results'][j]['mapLatitude'])
        longitude.append(result['searchResult']['paginationResult']['results'][j]['mapLongitude'])
        review_count.append(result['searchResult']['paginationResult']['results'][j]['reviewCount'])
        score_smile.append(result['searchResult']['paginationResult']['results'][j]['scoreSmile'])
        score_cry.append(result['searchResult']['paginationResult']['results'][j]['scoreCry'])
        score_overall.append(result['searchResult']['paginationResult']['results'][j]['scoreOverall'])
        bookmark_count.append(result['searchResult']['paginationResult']['results'][j]['bookmarkedUserCount'])

        holder_category = []
        holder_name = []
        for k in range(len(result['searchResult']['paginationResult']['results'][j]['categories'])):
            holder_category.append(result['searchResult']['paginationResult']['results'][j]['categories'][k]['categoryId'])
            holder_name.append(result['searchResult']['paginationResult']['results'][j]['categories'][k]['name'])
        category_id.append(holder_category)
        category_name.append(holder_name)
    print("Scraping page: " + str(i))
    
    i += 1

df = pd.DataFrame([name,review_url,district,district_id,category_id,category_name,price_UI,address,review_count,score_smile,score_cry,score_overall,bookmark_count,latitude,longitude]).transpose()
col = ['Name','Review URL','District','District ID','Category ID','Category Name','Price UI','Address','Review Count','Smile','Cry','Overall Score','Bookmark Count','Latitude','longitude']
df.columns = col

# Remove duplicates
df_master = pd.read_csv("assets/data/master_restaurant_urls.csv")

for i in df['Review URL']:
    # https://stackoverflow.com/questions/30944577/check-if-string-is-in-a-pandas-dataframe
    if df_master['Review URL'].str.contains(i).any():
        # https://stackoverflow.com/questions/36684013/extract-column-value-based-on-another-column-pandas-dataframe
        df_master.loc[df_master['Review URL'] == i, 'Smile'] = df.loc[df['Review URL'] == i, 'Smile'].iloc[0]
        df_master.loc[df_master['Review URL'] == i, 'Cry'] = df.loc[df['Review URL'] == i, 'Cry'].iloc[0]
        df_master.loc[df_master['Review URL'] == i, 'Overall Score'] = df.loc[df['Review URL'] == i, 'Overall Score'].iloc[0]
        df_master.loc[df_master['Review URL'] == i, 'Bookmark Count'] = df.loc[df['Review URL'] == i, 'Bookmark Count'].iloc[0]
        df_master.loc[df_master['Review URL'] == i, 'Review Count'] = df.loc[df['Review URL'] == i, 'Review Count'].iloc[0]
        
        # If there's duplicate, reduce the amount of duplicate reviews to scrape
        df.loc[df['Review URL'] == i, 'Review Count'] = df.loc[df['Review URL'] == i, 'Review Count'].iloc[0] - df_master.loc[df_master['Review URL'] == i, 'Review Count'].iloc[0]
    
    else:
        # https://stackoverflow.com/questions/39815646/pandas-append-dataframe-to-another-df
        df_master = df_master.append(df.loc[df['Review URL'] == i],ignore_index=True)

df_master.to_csv('assets/data/master_restaurant_urls.csv',encoding='utf-8',index=False)

review_urls = []

for k in range(len(df['Review Count'])):
    num_of_review_pages = math.ceil(df['Review Count'][k] / 15.0)

    for i in range(1,int(num_of_review_pages)):
        review_urls.append('https://www.openrice.com'+ str(df['Review URL'][k]) + '?page='+ str( i ))

# print review_urls
print("There is {} urls to scrape".format(len(review_urls)))
