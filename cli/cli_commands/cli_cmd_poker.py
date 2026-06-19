"""
Vibe Coded ... Yolo

TODO maybe: Persistent User Chips add self._user_db_ent.poker_chips = 500
"""
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from collections import Counter
import random

from cli.cli_modulBase import CliModulBase


class PokerState(Enum):
    IDLE = 0
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    SHOWDOWN = 5


@dataclass
class PokerHand:
    cards: list
    rank: int
    rank_name: str
    kickers: list = None


RANK_MAP = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']


class CliCmdPoker(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main)
        self._game = None
        self._chips_start = 500

    # ====================== Kartendarstellung ======================

    def _card_to_str(self, card):
        s = {'♠': '♠', '♥': '♥', '♦': '♦', '♣': '♣'}
        return f"{card[:-1]}{s.get(card[-1], card[-1])}"

    def _hand_to_str(self, hand_cards):
        return '  '.join(self._card_to_str(c) for c in hand_cards)

    def _hidden_card(self):
        return '[?]'

    # ====================== Deck & Evaluation ======================

    @staticmethod
    def _deck():
        return [r + s for r in RANKS for s in SUITS]

    @staticmethod
    def _evaluate_5(cards):
        if len(cards) != 5:
            return PokerHand(cards, -1, "Invalid", [])
        ranks = [c[:-1] for c in cards]
        suits = [c[-1] for c in cards]
        values = [RANK_MAP[r] for r in ranks]
        rc = Counter(values)
        sc = Counter(suits)
        sv = sorted(values, reverse=True)
        is_flush = len(sc) == 1
        def straight(vals):
            u = sorted(set(vals))
            if len(u) != 5:
                return False, 0
            if max(u) - min(u) == 4:
                return True, max(u)
            if set(u) == {14, 2, 3, 4, 5}:
                return True, 5
            return False, 0
        is_straight, sh = straight(sv)
        if is_flush and is_straight:
            if max(values) == 14:
                return PokerHand(cards, 9, "Royal Flush", [14])
            return PokerHand(cards, 8, "Straight Flush", [sh])
        if 4 in rc.values():
            q = [v for v, c in rc.items() if c == 4][0]
            k = [v for v in sv if v != q]
            return PokerHand(cards, 7, "Four of a Kind", [q] + k)
        if 3 in rc.values() and 2 in rc.values():
            t = [v for v, c in rc.items() if c == 3][0]
            p = [v for v, c in rc.items() if c == 2][0]
            return PokerHand(cards, 6, "Full House", [t, p])
        if is_flush:
            return PokerHand(cards, 5, "Flush", sv)
        if is_straight:
            return PokerHand(cards, 4, "Straight", [sh])
        if 3 in rc.values():
            t = [v for v, c in rc.items() if c == 3][0]
            k = [v for v in sv if v != t]
            return PokerHand(cards, 3, "Three of a Kind", [t] + k)
        pairs = [v for v, c in rc.items() if c == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            k = [v for v in sv if v not in pairs]
            return PokerHand(cards, 2, "Two Pair", pairs + k)
        if 2 in rc.values():
            p = [v for v, c in rc.items() if c == 2][0]
            k = [v for v in sv if v != p]
            return PokerHand(cards, 1, "One Pair", [p] + k)
        high = max(sv)
        hn = [k for k, v in RANK_MAP.items() if v == high][0]
        return PokerHand(cards, 0, f"High Card ({hn})", sv)

    @staticmethod
    def _best_hand(cards):
        best = None
        for combo in combinations(cards, 5):
            h = CliCmdPoker._evaluate_5(list(combo))
            if best is None or h.rank > best.rank or (h.rank == best.rank and h.kickers > best.kickers):
                best = h
        return best

    @staticmethod
    def _cmp_hands(h1, h2):
        if h1.rank != h2.rank:
            return h1.rank - h2.rank
        for a, b in zip(h1.kickers, h2.kickers):
            if a != b:
                return a - b
        return 0

    # ====================== KI-Gegner ======================

    def _ai_preflop_strength(self, hole):
        v = [RANK_MAP[c[:-1]] for c in hole]
        v.sort(reverse=True)
        pair = v[0] == v[1]
        suited = hole[0][-1] == hole[1][-1]
        if pair:
            return v[0]
        return v[0] + (0.5 if suited else 0) + (0.3 if v[0] > 11 and v[1] > 10 else 0)

    def _ai_decision(self, bet_amount, current_bet):
        g = self._game
        ai_cards = g['dealer_hand']
        all_cards = ai_cards + g['community']
        if len(all_cards) < 5:
            pf_strength = self._ai_preflop_strength(ai_cards)
            strength = pf_strength * 0.6
        else:
            hand = self._best_hand(all_cards)
            strength = hand.rank + (max(hand.kickers) / 20 if hand.kickers else 0)
        pot = g['pot']
        call_cost = current_bet - g['ai_bet']
        if call_cost <= 0:
            if strength > 4:
                return 'raise', 20
            if strength > 2:
                return 'bet', 10
            return 'check', 0
        pot_odds = call_cost / (pot + call_cost) if pot + call_cost > 0 else 1
        if strength > 3 or (strength > 1 and pot_odds < 0.3):
            if strength > 5 and random.random() < 0.4:
                return 'raise', min(call_cost * 2, g['dealer_chips'])
            return 'call', call_cost
        if random.random() < 0.1:
            return 'raise', call_cost
        return 'fold', 0

    # ====================== Spielverwaltung ======================

    def _new_game(self):
        chips = getattr(self._user_db_ent, 'poker_chips', self._chips_start)
        self._game = {
            'chips': chips,
            'dealer_chips': chips,
            'pot': 0,
            'player_bet': 0,
            'ai_bet': 0,
            'ai_acted': False,
            'state': PokerState.IDLE,
            'player_hand': [],
            'dealer_hand': [],
            'community': [],
            'last_action': '',
        }
        if self._user_db_ent and not hasattr(self._user_db_ent, 'poker_chips'):
            self._user_db_ent.poker_chips = self._chips_start

    def _save_chips(self):
        if self._user_db_ent and self._game:
            self._user_db_ent.poker_chips = self._game['chips']

    # ====================== Hauptkommando ======================

    def cmd_poker(self):
        self._decode_param(defaults=['', 0, 0, 0, 0, 0])
        if not self._parameter or str(self._parameter[0]).upper() in ['HELP', 'H']:
            return self._show_help()
        if str(self._parameter[0]).upper() == 'HANDS':
            return self._show_hand_ranking()
        if str(self._parameter[0]).upper() == 'HIGH':
            return self._show_highscore()
        if not self._game:
            self._new_game()
        if self._game['state'] == PokerState.IDLE:
            return self._start_new_round()
        return self._handle_ingame_input()

    # ====================== Spielstart + Streets ======================

    def _start_new_round(self):
        g = self._game
        g['pot'] = 0
        g['player_bet'] = 0
        g['ai_bet'] = 0
        g['community'] = []
        g['last_action'] = ''
        if g['chips'] <= 0:
            self._game = None
            return self._getTabStr_CLI('poker_no_chips')
        ante = min(10, g['chips'], g['dealer_chips'])
        g['chips'] -= ante
        g['dealer_chips'] -= ante
        g['pot'] += ante * 2
        deck = self._deck()
        random.shuffle(deck)
        g['player_hand'] = deck[:2]
        g['dealer_hand'] = deck[2:4]
        g['deck'] = deck[4:]
        g['state'] = PokerState.PREFLOP
        return self._show_table() + "\r\r" + self._get_prompt()

    def _deal_flop(self):
        g = self._game
        g['community'] = g['deck'][:3]
        g['deck'] = g['deck'][3:]
        g['state'] = PokerState.FLOP
        g['player_bet'] = 0
        g['ai_bet'] = 0
        g['ai_acted'] = False

    def _deal_turn(self):
        g = self._game
        g['community'].append(g['deck'][0])
        g['deck'] = g['deck'][1:]
        g['state'] = PokerState.TURN
        g['player_bet'] = 0
        g['ai_bet'] = 0
        g['ai_acted'] = False

    def _deal_river(self):
        g = self._game
        g['community'].append(g['deck'][0])
        g['deck'] = g['deck'][1:]
        g['state'] = PokerState.RIVER
        g['player_bet'] = 0
        g['ai_bet'] = 0
        g['ai_acted'] = False

    def _next_street(self):
        g = self._game
        g['player_bet'] = 0
        g['ai_bet'] = 0
        if g['state'] == PokerState.FLOP:
            self._deal_turn()
        elif g['state'] == PokerState.TURN:
            self._deal_river()
        elif g['state'] == PokerState.RIVER:
            return self._showdown()
        else:
            return self._showdown()
        return self._after_player_postflop()

    # ====================== Tabelle anzeigen ======================

    def _show_table(self, show_all=False):
        g = self._game
        out = self._getTabStr_CLI('poker_title')
        out += self._getTabStr_CLI('poker_table_header').format(g['chips'], g['dealer_chips'], g['pot'])
        out += self._getTabStr_CLI('poker_your_cards') + self._hand_to_str(g['player_hand']) + "\r"
        dlr = self._getTabStr_CLI('poker_dealer')
        if show_all:
            out += dlr + self._hand_to_str(g['dealer_hand']) + "\r"
        else:
            out += dlr + self._hidden_card() + "  " + self._card_to_str(g['dealer_hand'][1]) + "\r"
        if g['community']:
            out += self._getTabStr_CLI('poker_community') + self._hand_to_str(g['community']) + "\r"
        if g['state'] != PokerState.PREFLOP:
            player_hand = self._best_hand(g['player_hand'] + g['community'])
            out += self._getTabStr_CLI('poker_your_hand') + player_hand.rank_name + "\r"
        if g['last_action']:
            out += "\r" + g['last_action'] + "\r"
        return out

    def _get_prompt(self):
        return self._getTabStr_CLI('poker_prompt')

    # ====================== Spieler-Input ======================

    def _handle_ingame_input(self):
        if not self._parameter[0]:
            return self._show_table() + self._get_prompt()
        cmd = str(self._parameter[0]).upper()
        args = self._parameter[1:]
        if cmd == 'FOLD':
            return self._player_fold()
        elif cmd in ('CHECK',):
            g = self._game
            if g.get('ai_bet', 0) > g.get('player_bet', 0):
                return self._getTabStr_CLI('poker_cant_check')
            return self._player_bet(0)
        elif cmd in ('CALL',):
            g = self._game
            cost = g.get('ai_bet', 0) - g.get('player_bet', 0)
            if cost <= 0:
                return self._player_bet(0)
            return self._player_bet(cost)
        elif cmd == 'BET':
            try:
                amount = int(args[0]) if args else 10
                return self._player_bet(amount)
            except (ValueError, IndexError):
                return self._getTabStr_CLI('poker_invalid_bet')
        elif cmd == 'RAISE':
            try:
                amount = int(args[0]) if args else 20
                return self._player_bet(amount)
            except (ValueError, IndexError):
                return self._getTabStr_CLI('poker_invalid_bet')
        elif cmd in ('QUIT', 'END'):
            self._game = None
            return self._getTabStr_CLI('poker_quit')
        return self._getTabStr_CLI('poker_unknown_cmd')

    def _player_fold(self):
        g = self._game
        g['dealer_chips'] += g['pot']
        g['last_action'] = self._getTabStr_CLI('poker_player_folded')
        out = self._show_table(show_all=True) + "\r\r" + self._getTabStr_CLI('poker_dealer_wins_pot').format(g['pot']) + "\r"
        g['state'] = PokerState.IDLE
        self._save_chips()
        if g['chips'] > 0:
            out += self._getTabStr_CLI('poker_new_round')
        else:
            out += self._getTabStr_CLI('poker_no_chips_new_game')
        return out

    def _player_bet(self, amount):
        g = self._game
        amount = max(0, min(amount, g['chips']))
        ai_bet = g.get('ai_bet', 0)
        player_bet = g.get('player_bet', 0)
        call_cost = ai_bet - player_bet
        if amount > 0 and amount < call_cost and ai_bet > 0:
            return self._getTabStr_CLI('poker_must_call').format(ai_bet)
        actual = max(amount, call_cost)
        actual = min(actual, g['chips'])
        g['chips'] -= actual
        g['pot'] += actual
        g['player_bet'] = player_bet + actual
        if g['state'] == PokerState.PREFLOP:
            return self._after_player_preflop()
        return self._after_player_postflop()

    # ====================== Preflop ======================

    def _after_player_preflop(self):
        g = self._game
        ai_bet = g.get('ai_bet', 0)
        player_bet = g.get('player_bet', 0)
        diff = player_bet - ai_bet
        if diff == 0 and ai_bet == 0:
            g['last_action'] = self._getTabStr_CLI('poker_both_check')
            self._deal_flop()
            return self._after_player_postflop()
        if diff > 0:
            result = self._ai_decision(diff, player_bet)
            action, ai_amount = result
            if action == 'fold':
                g['chips'] += g['pot']
                return self._end_round(self._getTabStr_CLI('poker_dealer_folds'))
            ai_actual = min(ai_amount, g['dealer_chips'])
            g['dealer_chips'] -= ai_actual
            g['pot'] += ai_actual
            g['ai_bet'] = ai_bet + ai_actual
            if action == 'raise':
                g['last_action'] = self._getTabStr_CLI('poker_dealer_raised').format(ai_actual)
                out = self._show_table()
                out += "\r" + self._getTabStr_CLI('poker_dealer_raises_to').format(ai_actual, g['player_bet']) + "\r"
                out += self._getTabStr_CLI('poker_prompt')
                return out
            g['last_action'] = self._getTabStr_CLI('poker_dealer_called').format(ai_actual)
            self._deal_flop()
            return self._after_player_postflop()
        self._deal_flop()
        return self._after_player_postflop()

    # ====================== Postflop (FLOP / TURN / RIVER) ======================

    def _after_player_postflop(self):
        g = self._game
        ai_bet = g.get('ai_bet', 0)
        player_bet = g.get('player_bet', 0)
        if ai_bet > player_bet:
            g['last_action'] = self._getTabStr_CLI('poker_player_calls')
            return self._next_street()
        if player_bet > 0:
            result = self._ai_decision(0, player_bet)
            action, amount = result
            if action == 'fold':
                g['chips'] += g['pot']
                return self._end_round(self._getTabStr_CLI('poker_dealer_folds'))
            ai_actual = min(amount, g['dealer_chips'])
            g['dealer_chips'] -= ai_actual
            g['pot'] += ai_actual
            g['ai_bet'] = ai_actual
            if action == 'raise':
                g['last_action'] = self._getTabStr_CLI('poker_dealer_raised').format(ai_actual)
                out = self._show_table()
                out += "\r" + self._getTabStr_CLI('poker_dealer_raises_to').format(ai_actual, g['player_bet']) + "\r"
                out += self._getTabStr_CLI('poker_prompt')
                return out
            g['last_action'] = self._getTabStr_CLI('poker_dealer_called').format(ai_actual)
            return self._next_street()
        if g.get('ai_acted', False):
            return self._next_street()
        g['ai_acted'] = True
        result = self._ai_decision(0, 0)
        action, amount = result
        if action in ('bet', 'raise'):
            ai_actual = min(amount, g['dealer_chips'])
            g['dealer_chips'] -= ai_actual
            g['pot'] += ai_actual
            g['ai_bet'] = ai_actual
            g['last_action'] = self._getTabStr_CLI('poker_dealer_bets').format(ai_actual)
            return self._show_table() + "\r" + self._getTabStr_CLI('poker_dealer_bets_line').format(ai_actual) + "\r" + self._get_prompt()
        g['last_action'] = self._getTabStr_CLI('poker_both_check')
        return self._show_table() + self._get_prompt()

    # ====================== Showdown ======================

    def _showdown(self):
        g = self._game
        g['state'] = PokerState.SHOWDOWN
        player_best = self._best_hand(g['player_hand'] + g['community'])
        dealer_best = self._best_hand(g['dealer_hand'] + g['community'])
        out = self._show_table(show_all=True) + "\r\r"
        out += self._getTabStr_CLI('poker_player_hand_label').format(len(g['player_hand'] + g['community']), player_best.rank_name) + "\r"
        out += self._getTabStr_CLI('poker_dealer_hand_label').format(len(g['dealer_hand'] + g['community']), dealer_best.rank_name) + "\r\r"
        result = self._cmp_hands(player_best, dealer_best)
        if result > 0:
            g['chips'] += g['pot']
            out += self._getTabStr_CLI('poker_win').format(g['pot']) + "\r"
        elif result == 0:
            split = g['pot'] // 2
            g['chips'] += split
            g['dealer_chips'] += g['pot'] - split
            out += self._getTabStr_CLI('poker_tie').format(split) + "\r"
        else:
            g['dealer_chips'] += g['pot']
            out += self._getTabStr_CLI('poker_dealer_wins_showdown').format(dealer_best.rank_name) + "\r"
        self._save_chips()
        out += "\r" + self._getTabStr_CLI('poker_your_balance').format(g['chips']) + "\r"
        return self._end_round(extra=out)

    # ====================== Rundenende ======================

    def _end_round(self, msg='', extra=''):
        g = self._game
        if msg:
            out = extra + "\r # " + msg + "\r"
        else:
            out = extra
        g['state'] = PokerState.IDLE
        self._save_chips()
        if g['chips'] > 0:
            out += self._getTabStr_CLI('poker_new_round')
        else:
            out += self._getTabStr_CLI('poker_game_over')
        return out

    # ====================== Hilfeseiten ======================

    def _show_help(self):
        return self._getTabStr_CLI('poker_help')

    def _show_hand_ranking(self):
        return self._getTabStr_CLI('poker_hand_ranking_title')

    def _show_highscore(self):
        return self._getTabStr_CLI('poker_highscore_not_impl')
