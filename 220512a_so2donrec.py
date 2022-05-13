import bs4
import csv 
import re
import json
import pprint
import requests

#Test時にはGoogleColabにjsonのアップロード必要


# 自分の店の名前
nameMyShop=""
isTest=True

if isTest ==True:
  # json open load
  jopenitem = open('soldout2item.json', 'r', encoding='Shift_JIS')
  jitem = json.load(jopenitem)
  jopentown = open('soldout2town.json', 'r', encoding='UTF-8')
  jtown = json.load(jopentown)
  jopenshop = open('soldout2shop.json', 'r', encoding='UTF-8')
  jshop = json.load(jopenshop)
  jopenst = open('soldout2store.json', 'r', encoding='UTF-8')
  jst = json.load(jopenst)
  #print(repr(jopenitem))
  #print(repr(jopentown))
  #print(repr(jopenst))
elif isTest==False:
  jopentown = open('soldout2town.json', 'r', encoding='UTF-8')
  jtown = json.load(jopentown)

  urlItem = "https://so2-api.mutoys.com/master/item.json"
  session = requests.Session()
  data = session.get(urlItem)
  jitem = json.loads(data.text)
  urlStore = "https://so2-api.mutoys.com/json/sale/all.json"
  data = session.get(urlStore)
  jst = json.loads(data.text)
  urlShop = "https://so2-api.mutoys.com/json/shop/all.json"
  data = session.get(urlShop)
  jshop = json.loads(data.text)

def getItemid(name):
  jitemvals = jitem.values()
  for vitem in jitemvals:
    if vitem["name"] == name:
      ret=vitem["item_id"]
      exit
  return ret

def getItemname(id):
  jitemvals = jitem.values()
  for vitem in jitemvals:
    if vitem["item_id"] == id:
      ret=vitem["name"]
      exit
  return ret

def getShopName(name):
  for shop in jshop:
    if shop["shop_name"] == name:
      return shop

def getShopsItem(itemname):
  liShope=[]
  for vst in jst:
    if vst["item_id"] == getItemid(itemname):
      liShope.append(vst)
  return liShope

def getPos(shop):
  #shopエリア特定  
  jtowns = jtown.values()
  for town in jtowns:
    if town['area_id'] == shop['area_id']:
      shopTown=town
      exit
  posXshop=shop['pos_x']+shopTown['pos_x']
  posYshop=shop['pos_y']+shopTown['pos_y']
  return [posXshop,posYshop]

def getTransTime(shop):
  #(輸送時間[min]) ＝(0.15×(マンハッタン距離)^2+50)/(輸送速度[%])
  myShop=getShopName(nameMyShop)

  posMe=getPos(myShop)
  posShop=getPos(shop)
  trtime=( 0.15 * (abs(posShop[0]-posMe[0])+abs(posShop[1]-posMe[1]) ) **2 +50 ) / 100
  ret = trtime
  return ret

# アイテムについて、輸送時間が一定以下の店を取得
# html(寄付ページ) 解析
soup = bs4.BeautifulSoup(open('soldout2_donrec.html'), 'html.parser')
itemsets=(soup.find_all(style =re.compile("width: 12rem; font-size: small; display: inline-block; text-align: left;")))
between=15
for num in range (0,76,between):
  print("{0}分以上{1}分未満".format(num,num+between))
  for itemset in itemsets:
    #itemset==寄付のセット
    #print(itemset.text)
    buyitemsets=[]
    items=itemset.find_all(class_ =re.compile("icon icon-item icon-item-"))
    if not itemset.text.startswith("[0]"):
      continue
    itemYes=False
    for item in items:
      #短時間のitemが一個も無かったら次のitem
      #itemが全部短時間なら出力
      itemShops=getShopsItem(item["title"])
      shopYes=False
      for shop in itemShops:
        #短時間のshopが一個も無かったら次のitem
        liItemSale=[]
        transTime=getTransTime(shop)
        if num <= getTransTime(shop) < num+between:
          liItemSale.append(getItemname(shop["item_id"]))
          liItemSale.append("{:,}".format((shop["price"])))
          liItemSale.append("{0} 分".format(transTime))
          buyitemsets.append(liItemSale)
          shopYes=True
      if shopYes==False:
        break
    if shopYes==True:
      print(itemset.text)
      for item in items:
        print(item["title"])
      for b in buyitemsets:
        print(b)

# csvlist = []
# for link in links:
#     sample_txt = link.text
#     csvlist.append(sample_txt)

# # CSVファイルを開く。ファイルがない場合は新規作成
# f = open("output_sample.csv", "w")
# writecsv = csv.writer(f, lineterminator='\n')

# writecsv.writerow(csvlist) # 出力

# f.close()