# -*- coding: utf-8 -*-
"""
Spyder Editor
@pspandya
This is a temporary script file.
"""

#with open('D:\Python-Working-Directory\Project\yelp_academic_dataset_business.json') as data_file:    
#    data = json.load(data_file)


import json
import re                               #for removing non-alphabets from the user reviews
from datetime import date
import xlsxwriter                       #for data visulization purpose; to convert dictionary to csv
from scipy import stats                 #for t-test and fisher test
from nltk.corpus import wordnet as wn #for fetching food item names
from nltk.corpus import stopwords     #to remove stopwords

# not all consecutive buckets have p<0.05 | find Up and Down

#output_file=open('testReview.json', 'w')
newdata = {}
i = 0
data = []
finalData=[]
bidDataFB = {}
bidDataFBName=[]
bidDataFCK=[]
like=[]
tuid={}
final={}
biddate={}
final_data={}
atest_data={}
ttest_dict={}
BucketmasterReview={}
bucketReviews = {}   
bucketReviewCount = {}
dataWithWordFreq={}
dictFisherAns={}
# food = {}

print("file start")

def businessid():                       #procedure for data fetching and parsing
    with open('yelp_academic_dataset_business.json') as i:  
        for line in i:
            data = json.loads(line)        
            if 'Restaurants' in data['categories']:      #As suggested by proffesor, we chose businesses having restaurants as a category
                if data['review_count'] > 300:          #Only those restaurants are considered which has review count greater then 300 so that we can work on lager raw dataset
                    if data['open'] == True:            #We saw that yelp dataset's businesses have attribute:open indicting current status of business; so we're considering only currently open restaurants 
                        bidDataFB[data['business_id']] = data['name']
        print 'PARTH PANDYA'

#?    
def tip():
    with open('yelp_academic_dataset_tip.json') as i:
        for line in i:
            data = json.loads(line)        
            if bidDataFB.has_key(data['business_id']):
                tuid[data['business_id']] = data['user_id']
                print(data['text'])                

def review():
    with open('yelp_academic_dataset_review.json') as i:
        for line in i:
            data = json.loads(line)  
            if bidDataFB.has_key(data['business_id']):
                row = []                      
                row.insert(1, data['date'].encode('ascii','ignore'))
                row.insert(2, re.sub("[^a-zA-Z]+", " ", str(data['text'].replace('"', r' ').encode('ascii', 'ignore'))))
                row.insert(3, data['stars'])
                row.insert(4, bidDataFB.get(data['business_id']).encode('ascii','ignore'))
                biddate.setdefault(data['business_id'], []).append(row)
                
    print("Review")
    
def dataModel():
    for item, value in bidDataFB.iteritems():
        row = biddate.get(item)
        newRow = sorted(row,key=lambda l:l[0], reverse=True)
        final[item] = newRow

def d(s):
    [year, month, day] = map(int, s.split('-'))
    return date(year, month, day)

def days(start, end):
    return (d(end) - d(start)).days
  
def buckets():
    for item, value in final.iteritems():
        row = final.get(item)
        bucket={}
        mainDate = row[0][0]
        i = 0
        for items in row:
            delta = days(items[0], mainDate)
            try:
                if delta > 90:
                    mainDate = items[0]
                    i += 1
                newRow = items
                bucket.setdefault(i, []).append(newRow)
            except: 
                print('153')
        final_data[item] = bucket

def f_ttest():
    for key, value in final_data.iteritems():
        bucketStar = {}
        for item in final_data[key]:
            for tuples in final_data[key][item]:
                bucketStar.setdefault(item, []).append(tuples[2])
        ttest_bkid = {}
        for bucketId, star in bucketStar.iteritems():
            value = bucketStar.get(bucketId + 1, None)
            if value is not None:
                t, p = stats.ttest_ind(star, bucketStar.get(bucketId + 1), equal_var = False)
                if p < 0.05:
                    ttest_bkid[bucketId] = final_data[key][bucketId]
                    ttest_bkid[bucketId+1] = final_data[key][bucketId+1]
        if bool(ttest_bkid):
            ttest_dict[key.encode('ascii','ignore')] = ttest_bkid

def combineReviewofBuckets():
    for key, value in ttest_dict.iteritems():
        reviewList = {}
        for item in ttest_dict[key]:
            for tuples in ttest_dict[key][item]:
                reviewList.setdefault(item, []).append(tuples[1])
            ' '.join(reviewList[item])
        bucketReviews[key] = reviewList
    #print(bucketReviews)
        #bucketReviews[key.encode('ascii','ignore')] = reviewList
   
        

def exportExcel():                         #Function for exporting csv files for easier data visulization
    workbook = xlsxwriter.Workbook('data_wordFrequency.xlsx')
    worksheet = workbook.add_worksheet()

    row = 0
    col = 0

    for key in dataWithWordFreq.keys():
        row += 1
        worksheet.write(row, col, key)
        for item in dataWithWordFreq[key]:
            worksheet.write(row, col + 1, item)
            row += 1
            print(item)
            for tuples in dataWithWordFreq[key][item]:
                print(tuples)
                worksheet.write_string(row, col + 2, tuples)
                worksheet.write_string(row, col + 3, bucketReviews[key][item][tuples])
                row += 1
            """
            for tuples in bucketReviews[key][item]:
                worksheet.write_string(row, col + 2, tuples[0])
                worksheet.write_string(row, col + 3, tuples[1])
                worksheet.write_string(row, col + 4, str(tuples[2]))
                worksheet.write_string(row, col + 5, tuples[3])
                row += 1
            """
    print("end")
    workbook.close()
    
def exportTxt():
    with open('sortedFreqWord.txt', 'w') as file_handler:
       for item, value in dictFisherAns.iteritems():
           file_handler.write("%s %s\n" % (item, value))

def exportTxt2(bucketReviewCount):
    with open('bucketReviewCount.txt', 'w') as file_handler:
       for item, value in bucketReviewCount.iteritems():
           file_handler.write("%s %s\n" % (item, value))

def wellknownfooditem():
    food = wn.synset('food.n.02')
    return(list(set([w.lower().encode('ascii','ignore') for s in food.closure(lambda s:s.hyponyms()) for w in s.lemma_names()])))

def loadLexicon(fname):
    newLex=set()
    lex_conn=open(fname)
    for line in lex_conn:
        newLex.add(line.strip())
    lex_conn.close()
    return newLex

def freqWords():
    bucketfreq={}
    stopLex=set(stopwords.words('english'))
    restaurentWords = wellknownfooditem()
    for item, value in bucketReviews.iteritems():
        bucketfreq={}
        reviewCount = {}
        i=0
        for key in bucketReviews[item]:
            wordFreq = {}
            i=0
            for tuples in bucketReviews[item][key]:
                i+=1
                tuples = tuples.lower().strip()                
                words = tuples.split(' ')
                for word in words:                 
                    if word=='' or word in stopLex:
                        continue
                    elif word in restaurentWords: 
                        wordFreq[word] = wordFreq.get(word,0)+1
                bucketfreq[key] = wordFreq
                reviewCount[key]= i
        dataWithWordFreq[item] = bucketfreq
        bucketReviewCount[item] = reviewCount     
    #exportTxt2(bucketReviewCount)
    
        #print(bucketReviewCount)

                    #print(word)
			#if word=='' or word not in stopLex:continue # ignore empty words and stopwords

def fisherTest():
    for bid, buck in dataWithWordFreq.iteritems():
        print(bid)
        for buckets in dataWithWordFreq[bid]:
            value = dataWithWordFreq[bid].get(buckets + 1, None)
            if value is not None:
                filterdData={}                
                commonKeys = dataWithWordFreq[bid][buckets].viewkeys() & dataWithWordFreq[bid][buckets + 1].viewkeys()
                if bool(set(commonKeys)):
                    for ck in commonKeys:
                        b = dataWithWordFreq[bid][buckets].get(ck)
                        c = bucketReviewCount[bid][buckets]                       
                        d = dataWithWordFreq[bid][buckets + 1].get(ck)
                        e = bucketReviewCount[bid][buckets + 1]
                        t, p = stats.fisher_exact([[b,c],[d,e]])
                        if p < 0.05:
                            print("bucket: " +str(buckets) + " and next B: " + str(buckets +1))
                            print(ck)
                            print("p value: " +str(p))
                            filterdData.setdefault(buckets, []).append(ck)
                    dictFisherAns.setdefault(bid, []).append(filterdData)
                       
def fileGenerater():
    for key, value in dictFisherAns.iteritems():
        value = dictFisherAns.get(key, None)
        if value is not None: 
            resultbusiness = ttest_dict.get(key)
            for item, value in resultbusiness.iteritems():
                with open(str(resultbusiness[item][0][3])+'.txt', 'w') as file_handler:
                    for result in dictFisherAns[key]:
                        file_handler.write("Changpoints detected in Restaurent Items: %s\n from date: %s to %s" % (str(dictFisherAns[key][result]), str(resultbusiness[item][dictFisherAns.get(key)][0]), str(resultbusiness[item][dictFisherAns.get(key+1)][0])))
"""                    
                    for value in resultbusiness[item]:
                        file_handler.write("%s\n %s\n %s\n" % (value[0], value[1], value[2]))
"""                        
            
if __name__=='__main__':
    #print(wellknownfooditem())
    
    businessid()
    print("now open")
    review()
    print("after open")
    dataModel()
    print("after DataModel")
    buckets()
    print("T-Test")
    f_ttest()
    print("Review Combining")
    combineReviewofBuckets()    
    print("frequency of words")
    freqWords()
    print("Fisher test start")
    fisherTest()
    print("Export Start")
    #fileGenerater()
    exportTxt()
    #exportExcel()    
    print("Export Complete")
    print("File End")
    