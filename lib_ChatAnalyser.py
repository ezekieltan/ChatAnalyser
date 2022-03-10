import pandas as pd
import chatReader
import re
import datetime
import string
import json
class ChatAnalyser:
    def __init__(self, paths):
        messages = []
        for path in paths:
            subMessages = chatReader.readChat(path)
            messages = messages + subMessages
            
        self.df = pd.DataFrame(messages).set_index('id')
        self.parties = self.df['from'].drop_duplicates().dropna().tolist()
        self.df['length'] = self.df['text'].str.len()
        self.df['caps'] = self.df['text'].str.count(r'[A-Z]')
        self.df['count'] = 1

        self.df['emoji'] = self.df['text'].apply(lambda s: len(re.findall(r'[\U0001f600-\U0001f650]', s)))

        count = lambda l1,l2: sum([1 for x in l1 if x in l2])
        self.df['punctuation'] = self.df['text'].apply(lambda s: count(s, string.punctuation))

        tempDateWorker = self.df["dateTime"] - datetime.timedelta(hours=6)
        self.df['date'] = tempDateWorker.dt.floor('d')

        self.df['timeDiff'] = self.df['dateTime'].diff()
        #df.drop('text',axis=1).drop('from',axis=1)

        swaps = {}
        count = 0
        for index, row in self.df.iterrows():
            currentDate = row['date']
            currentFrom = row['from']
            if(currentDate not in swaps):
                swaps[currentDate] = -1
            if(count>1 and prevFrom !=currentFrom):
                swaps[currentDate] = swaps[currentDate] + 1
            prevDateTime = currentDate
            prevFrom = currentFrom
            count = count + 1
            
        swapDf = pd.DataFrame(swaps, index=['swaps']).T
        self.dateSummary = self.df.groupby(['date']).sum()
        self.dateSummary['swaps'] = swapDf['swaps']
        self.dateSummary['swapsPerCharacter'] = self.dateSummary['swaps']/self.dateSummary['length']
        self.chatSpan = (pd.to_datetime(min(self.df['dateTime'])).date(),pd.to_datetime(max(self.df['dateTime'])).date())
    def getBasicStats(self):
        return self.df.groupby(['from']).sum()
    def getCharRatio(self):
        basicStats = self.getBasicStats()
        return basicStats['length'][0]/basicStats['length'][1]
    def getTotalCharacters(self):
        return self.getBasicStats()['length'].sum()
    def getActivityPerParty(self):
        charsPerPersonOverTime = self.df.groupby(['from','date']).sum()['length']
        return charsPerPersonOverTime.reset_index()
    def getRatio(self, days):
        dfDateFrom = self.df.groupby(['date','from']).sum().reset_index()
        one = dfDateFrom[dfDateFrom['from']==self.parties[0]].set_index(['date'])
        two = dfDateFrom[dfDateFrom['from']==self.parties[1]].set_index(['date'])
        joined = one.join(two, lsuffix='_one', rsuffix='_two', how='outer')[['length_one', 'length_two']].fillna(0)
        #joined = joined.reindex(pd.date_range(chatSpan[0], chatSpan[1]), fill_value=0)
        joined.index.names = ['date']
        joinedRolling = joined.rolling(days).sum()
        joinedRolling['ratio'] = joinedRolling['length_one']/joinedRolling['length_two']
        return joinedRolling.reset_index()
    def getLongestGaps(self):
        return self.df.sort_values('dateTime').dateTime.diff().sort_values().to_frame().join(self.df,lsuffix='_gap')[['dateTime_gap','dateTime', 'from','text']]
    def getDf(self):
        return self.df
        