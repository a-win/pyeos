import os
import time
import struct

import wallet
import eosapi
import initeos

from eosapi import N
from tools import cpp2wast

from common import prepare, Sync, producer

print('please make sure you are running the following command before test')
print('./pyeos/pyeos --manual-gen-block --debug -i')

def init(wasm=False):
    def init_decorator(func):
        def func_wrapper(*args, **kwargs):
            if wasm:
                prepare('native', 'native.wast', 'native.abi', __file__)
            else:
                prepare('native', 'native.py', 'native.abi', __file__)
            return func(*args, **kwargs)
        return func_wrapper
    return init_decorator

@init()
def test(msg='hello,world'):
    with producer:
        r = eosapi.push_action('native', 'sayhello', msg, {'native':'active'})
        print(r)
        assert r

@init()
def deploy(debug=True):
    sync = Sync('native', _dir=os.path.dirname(__file__), _ignore=['t.py', 'native.py'])
    if debug:
        sync.deploy_native('eosio.token', 0, '../contracts/eosio.token/libeosiotokend.dylib')
    else:
        sync.deploy_native('eosio.token', 0, '../contracts/eosio.token/libeosiotoken.dylib')

@init()
def test2(count=100):
    actions = []

    for i in range(count):
        action = ['eosio.token', 'issue', {'eosio':'active'}, {"to":"eosio","quantity":"0.0100 EOS","memo":""}]
        actions.append(action)
#        msg = {"issuer":"eosio","maximum_supply":"10000000000.0000 EOS"}
#        action = ['eosio.token', 'create', {'eosio.token':'active'}, msg]
        actions.append(action)

    ret, cost = eosapi.push_actions(actions, True)
    assert ret
    print('total cost time:%.3f s, cost per action: %.3f ms, actions per second: %.3f'%(cost/1e6, cost/count/1000, 1*1e6/(cost/count)))

@init()
def test3():
    with producer:
        msg = {"issuer":"eosio","maximum_supply":"10000000000.0000 EOS"}
        r = eosapi.push_action('eosio.token', 'create', msg, {'eosio.token':'active'})
        print(r)
        assert r
