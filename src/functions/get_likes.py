#!/use/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse, os, sys, logging, datetime, json, re, traceback
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "vendor"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "utils"))

import time
import requests
import urllib.parse
from time import sleep
from operator import itemgetter
import csv

HEADERS = {
  # ':authority' : 'www.instagram.com',
  # ':method' : 'GET',
  # ':path' : '/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%228462316305%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Afalse%2C%22first%22%3A24%7D',
  # ':scheme' : 'https',
  'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding' : 'gzip, deflate, br',
  'accept-language' : 'ja,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
  'cache-control' : 'max-age=0',
  'cookie' : 'rur=FRC; ig_did=D4CA304B-379B-4826-8F3C-0DB63D4D3E3C; mid=XqmSFAALAAHUyNQ1mpF8GLaMffaB; csrftoken=wwUF8a1l41O3GSqCR7oReySqWJLOJ42C; ds_user_id=34582230805; sessionid=34582230805%3AGSZkQH6LLvEH76%3A27; urlgen="{\"124.219.171.153\": 2527}:1jTo2w:Tm4hdCMHELh879tSwccGl85SyQ4"',
  'sec-fetch-mode' : 'navigate',
  'sec-fetch-site' : 'none',
  'sec-fetch-user' : '?1',
  'upgrade-insecure-requests' : '1',
  'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
}

def lambda_handler(event, context):

  print("処理を開始します")
  t1 = time.time()

  isFirst = True
  hasNext = False
  endCursor = None
  postList = []

  while True:

    if isFirst:
      url = 'https://www.instagram.com/explore/tags/rgblue%E3%82%B9%E3%83%88%E3%83%83%E3%82%AF%E3%83%95%E3%82%A9%E3%83%88%E3%82%B3%E3%83%B3/?hl=ja'
      isFirst = False

      response = requests.get(url)
      sharedData = re.findall(r'<script type="text\/javascript">window._sharedData = (.*);<\/script>', response.text)
      jsonData = json.loads(sharedData[0])

      pageInfo = jsonData['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['page_info']
      hasNext = bool(pageInfo['has_next_page'])
      endCursor = pageInfo['end_cursor']

      list = jsonData['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
      # print(list)

    else:
      url = 'https://www.instagram.com/graphql/query/?query_hash=7dabc71d3e758b1ec19ffb85639e427b&variables='
      queryVar = '{"tag_name":"rgblueストックフォトコン","first":12,"after":"%s"}' % (endCursor)
      escapeQueryVar = urllib.parse.quote(queryVar)

      response = requests.get(url + escapeQueryVar, headers = HEADERS)
      jsonData = response.json()

      pageInfo = jsonData['data']['hashtag']['edge_hashtag_to_media']['page_info']
      hasNext = bool(pageInfo['has_next_page'])
      endCursor = pageInfo['end_cursor']

      list = jsonData['data']['hashtag']['edge_hashtag_to_media']['edges']
      # print(list)

    postList = checkPosts(list, postList)

    if hasNext:
      # break
      sleep(3)
    else:
      break

  t2 = time.time()
  elapsed_time = t2 - t1

  print("投稿についてのLike数取得が完了しました")
  print(f"経過時間: {elapsed_time}")
  print(f"投稿数: {len(postList)}")
  print("取得データに対し、ユーザネームの取得を行います")

  sortedResults = sorted(postList, key=itemgetter("likeNum"), reverse=True)

  results = []
  for value in sortedResults:
    try:
      userName = getUserName(value["shortCode"])
      value["userName"] = userName
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      results.append(value.copy())
      sleep(1)
    except:
      sleep(10)
      userName = getUserName(value["shortCode"])
      value["userName"] = userName
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      results.append(value.copy())
      sleep(1)

  # print(results)
  for value in results:
    print(value)

def checkPosts(list, postList):
  for node in list:
    print(node['node'])
    item = {
      "userId": node['node']['owner']['id'],
      "shortCode": node['node']['shortcode'],
      "likeNum": node['node']['edge_liked_by']['count']
    }
    postList.append(item.copy())
    print("id: " + node['node']['owner']['id'] + " / like num: " + str(node['node']['edge_liked_by']['count']))

  return postList

def getUserName(shortCode):
  url = f"https://www.instagram.com/p/{shortCode}/"
  print(f"https://www.instagram.com/p/{shortCode}/")

  response = requests.get(url, headers = HEADERS)
  data = re.findall(r'<script type="text/javascript">window.__additionalDataLoaded\(\'/p/%s/\',(.*)\);<\/script>' % shortCode, response.text)
  jsonData = json.loads(data[0])
  # print(jsonData['graphql']['shortcode_media']['owner']['username'])

  return jsonData['graphql']['shortcode_media']['owner']['username']

if __name__ == "__main__":
  lambda_handler(None, None)