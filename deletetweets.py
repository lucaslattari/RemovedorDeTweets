import subprocess

def installPackage(pkg):
    subprocess.check_call(["python", '-m', 'pip', 'install', pkg])
    subprocess.check_call(["python", '-m', 'pip', 'install',"--upgrade", pkg])

installPackage('tweepy')

import tweepy
import webbrowser
from tqdm import tqdm
from datetime import datetime, timedelta
import time
import configparser
import sys

#insira as chaves da API do Twitter aqui embaixo
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
days_to_keep = 365
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

def oauth_login(consumer_key, consumer_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_url = auth.get_authorization_url()

    print("Vou abrir uma janela do seu navegador. Logue-se por ela no Twitter, autorize o uso desse app.")
    webbrowser.open(auth_url)
    verify_code = input("Digite o código de verificação informado pelo Twitter > ") 
    auth.get_access_token(verify_code)
    
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

def log_tweep_error(tweep_error):
    if tweep_error.api_code:
        if tweep_error.api_code == 32:
            print("\nError: invalid API authentication tokens")
        elif tweep_error.api_code == 34:
            print("\nError: requested object (user, Tweet, etc) not found")
        elif tweep_error.api_code == 64:
            print("\nError: your account is suspended and is not permitted")
        elif tweep_error.api_code == 130:
            print("\nError: Twitter is currently in over capacity")
        elif tweep_error.api_code == 131:
            print("\nError: internal Twitter error occurred")
        elif tweep_error.api_code == 135:
            print("\nError: could not authenticate your API tokens")
        elif tweep_error.api_code == 136:
            print("\nError: you have been blocked to perform this action")
        elif tweep_error.api_code == 179:
            print("\nError: you are not authorized to see this Tweet")
        elif tweep_error.api_code == 404:
            print("\nError: The URI requested is invalid or the resource requested, such as a user, does not exist. ")
        elif tweep_error.api_code == 429:
            print("\nError: request cannot be served due to the app rate limit having been exhausted for the resource.")
        else:
            print("\nError: error while using the REST API:", tweep_error)
    else:
        print("\nError with Twitter:", tweep_error) 

def batch_delete(api, rodarsemperguntar):
    if rodarsemperguntar != 's':
        escolha = input("Você deseja deletar tweets antigos? Digite s para fazer isso e qualquer coisa pra não fazer isso > ")
    else:
        escolha = 's'
    if(escolha == 's'):
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        while True:
            if rodarsemperguntar != 's':
                confirmarAntesDeDeletarTweets = input("Você deseja confirmar antes de remover cada tweet? Digite s para sempre confirmar antes de remover e qualquer outra coisa em caso contrário > ")
                if(confirmarAntesDeDeletarTweets != 's'):
                    confirmarAntesDeDeletarTweets = input("Tem certeza? SE VOCÊ APERTAR QUALQUER COISA DIFERENTE DE s, SEUS TWEETS SERÃO REMOVIDOS SEM CONFIRMAÇÃO > ")
            else:
                confirmarAntesDeDeletarTweets = 'n'
            print("Buscando tweets a serem removidos", end =" ")

            tweetsDeletados = 0
            iterations = 0
            for tweet in tweepy.Cursor(api.user_timeline).items():
                try:
                    if iterations % 35 == 0:
                        print('.', end =" ")
                    if tweet.created_at < cutoff_date:
                        if confirmarAntesDeDeletarTweets == 's':
                            print("Texto do tweet:", tweet.text.translate(non_bmp_map))
                            print("Data do tweet:", tweet.created_at)
                            escolha = input("Deseja apagar esse tweet? Responda s para sim e qualquer outra coisa para não apagar > ")
                            if escolha == 's':
                                api.destroy_status(tweet.id)
                                print ("Apaguei tweet com o id: ", tweet.id, end =" ")
                                tweetsDeletados += 1
                        else:
                            api.destroy_status(tweet.id)
                            print ("Apaguei tweet com o id:", tweet.id, end =" ")
                            tweetsDeletados += 1                
                except tweepy.TweepError as e:
                    log_tweep_error(e)

                iterations += 1
            print("\nForam deletados", tweetsDeletados, "tweets.")
            break
 
    if rodarsemperguntar != 's':
        escolha = input("Você deseja deletar likes antigos? Digite s para fazer isso e qualquer coisa pra não fazer isso > ")
    else:
        escolha = 's'
    if escolha == 's':
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        while True:
            if rodarsemperguntar != 's':
                confirmarAntesDeDescurtirTweets = input("Você deseja confirmar antes de remover cada curtida? Digite s para sempre confirmar antes de remover e qualquer outra coisa em caso contrário > ")
                if confirmarAntesDeDescurtirTweets != 's':
                    confirmarAntesDeDescurtirTweets = input("Tem certeza? SE VOCÊ DIGITAR QUALQUER COISA DIFERENTE DE s, SUAS CURTIDAS SERÃO REMOVIDAS SEM PRÉVIO AVISO > ")
            else:
                confirmarAntesDeDescurtirTweets = 'n'

            print("Buscando curtidas de tweets a serem removidas", end =" ")
            tweetsDesfavoritados = 0
            iterations = 0
            for tweet in tweepy.Cursor(api.favorites).items():
                try:
                    if iterations % 35 == 0:
                        print('.', end =" ")
                    if tweet.created_at < cutoff_date:
                        if confirmarAntesDeDescurtirTweets == 's':
                            print("Texto do tweet:", tweet.text.translate(non_bmp_map))
                            print("Data do tweet:", tweet.created_at)
                            escolha = input("Deseja descurtir esse tweet? Responda s para sim e qualquer outra coisa para não remover > ")
                            if escolha == 's':
                                api.destroy_favorite(tweet.id)
                                print ("Descurti tweet com o id:", tweet.id, end =" ")
                                tweetsDesfavoritados += 1
                        else:
                            api.destroy_favorite(tweet.id)
                            print ("Descurti tweet com o id:", tweet.id, end =" ")
                            tweetsDesfavoritados += 1
                except tweepy.TweepError as e:
                    log_tweep_error(e)

                iterations += 1
            print("\nForam descurtidos", tweetsDesfavoritados, "tweets.")
            break
            
if __name__ == "__main__":
    with open('settings.ini', 'r') as file:
        parser = configparser.ConfigParser()
        parser.read('settings.ini')
        chaveApi = input("Informe chave da API do Twitter. Para usar a padrão, apenas aperte [ENTER] > ")
        if chaveApi:
            CONSUMER_KEY = chaveApi
        chaveApi = input("Informe chave secreta da API do Twitter. Para usar a padrão, apenas aperte [ENTER] > ")
        if chaveApi:
            CONSUMER_SECRET = chaveApi
        for section in parser.sections():
            for key, value in parser.items(section):
                if(key == 'diasanterioresamanter'):
                    diasAManter = input("Preciso que você me diga quantos dias para trás você quer manter. Por exemplo, se você informar 7 dias, apenas os tweets e likes mais antigos do que uma semana serão listados para remoção. O valor padrão é 365 > ")
                    if diasAManter:
                        days_to_keep = int(diasAManter)
                    else:
                        days_to_keep = int(value)
                elif(key == 'rodarsemperguntar'):
                    api = oauth_login(CONSUMER_KEY, CONSUMER_SECRET)
                    print ("Autenticado como: %s" % api.me().screen_name)

                    batch_delete(api, value)
