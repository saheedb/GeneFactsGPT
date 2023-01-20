"""
Prompts ChatGPT with a randomly selected gene from a pre-defined list at
random intervals and posts the response to twitter @GeneFactsGPT
"""
from random import choice
from time import sleep
from math import ceil
import tweepy
import openai
import json


def main() -> None:
    # json file with gene names and prompt phrases
    query_data = open('query_data.json', 'r')

    # json file with secret keys and tokens for twitter and openai access
    key_data = open('genefacts_keys.json', 'r')

    # load data dictionaries
    query_dict = json.load(query_data)
    key_dict = json.load(key_data)

    # create separate lists for gene names and prompt phrases
    query_phrases = query_dict['phrases']
    genes = query_dict['genes']

    # close input files
    query_data.close()
    key_data.close()

    # get get the number of genes and phrases
    # (to be used for randomization)
    n_genes = len(genes)
    n_phrases = len(query_phrases)

    # set openai secret info
    openai.organization = key_dict['openai_org']
    openai.api_key = key_dict['openai_key']

    # create twitter client with secret info
    client = tweepy.Client(bearer_token=key_dict['bearer_token'],
                           consumer_key=key_dict['consumer_key'],
                           consumer_secret=key_dict['consumer_key_secret'],
                           access_token=key_dict['access_token'],
                           access_token_secret=key_dict['token_secret'])

    # specify posting interval range in seconds
    r = range(30, 60)

    # main loop to run indefinitely
    while True:
        # sleep for chosen amount of time
        sec_sleep = choice(r)
        print('\nsleeping for', sec_sleep, 'seconds')
        sleep(sec_sleep)

        # build chatGPT query statement using a random phrase and a random gene
        query = ' '.join([query_phrases[choice(range(0, n_phrases))], genes[choice(range(0, n_genes))]])

        # query chatGPT with statement
        gpt_response = generate_response(query)
        print(gpt_response, '\n')

        # estimate number of tweets needed to post the chatGPT response
        # tweets are limited to 280 characters
        n_tweets = ceil(len(gpt_response) / 250)

        # create list of tweet words
        tweet_words = gpt_response.split()

        # count the number of tweet words
        n_words = len(tweet_words)

        # determine number of words in each tweet
        words_per_tweet = ceil(n_words / n_tweets)

        # create list of tweets for the chatGPT response
        tweets = [tweet_words[i:i + words_per_tweet] for i in range(0, len(tweet_words) + 1, words_per_tweet)]

        # post first tweet
        twit_response = client.create_tweet(text=' '.join(tweets[0]))

        # respond to first tweet then each subsequent tweet until the entire response is posted
        for i in range(1, n_tweets):
            twit_response = client.create_tweet(text=' '.join(tweets[i]), in_reply_to_tweet_id=twit_response.data['id'])


def generate_response(prompt) -> str:
    model_engine = 'text-davinci-003'
    prompt = f'{prompt}'

    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message.strip()


if __name__ == '__main__':
    main()
