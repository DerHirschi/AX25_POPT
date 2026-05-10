from dataclasses import dataclass
from enum import Enum
import random

from cli.cli_modulBase import CliModulBase


class PokerState(Enum):
    IDLE = 0
    DEAL = 1
    BET1 = 2
    DRAW = 3
    BET2 = 4
    SHOWDOWN = 5


@dataclass
class PokerHand:
    cards: list
    rank: int          # 0 = High Card ... 9 = Royal Flush
    rank_name: str


class CliCmdPoker(CliModulBase):
    def __init__(self, cli_main):
        super().__init__(cli_main)
        self._game = None
        self._chips_start = 500

        # Unicode Karten + Fallback
        self._use_unicode = True  # Kann später pro User gespeichert werden

    # ====================== Hilfsfunktionen ======================

    def _card_to_str(self, card: str):
        """Karte schön darstellen (Unicode oder ASCII-Fallback)"""
        if not self._use_unicode:
            return card  # z.B. "AS", "KD", ...

        suits = {'♠': '♠', '♥': '♥', '♦': '♦', '♣': '♣'}
        rank = card[:-1]
        suit = card[-1]
        return f"{rank}{suits.get(suit, suit)}"

    @staticmethod
    def _deck():
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        return [r + s for r in ranks for s in suits]

    @staticmethod
    def _evaluate_hand(cards: list):
        """Vollständige Poker-Hand Bewertung (5-Card Draw)"""
        if len(cards) != 5:
            return PokerHand(cards, 0, "Invalid")

        # Mapping: Karte -> Wert + Farbe
        rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                    '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

        ranks = [card[:-1] for card in cards]
        suits = [card[-1] for card in cards]
        values = [rank_map[r] for r in ranks]

        # Häufigkeiten der Ränge
        from collections import Counter
        rank_count = Counter(values)
        suit_count = Counter(suits)

        sorted_values = sorted(values, reverse=True)
        is_flush = len(suit_count) == 1

        # Straight erkennen (inkl. Wheel: A-5)
        def is_straight(vals):
            if len(set(vals)) != 5:
                return False
            if max(vals) - min(vals) == 4:
                return True
            # Wheel Straight: A-2-3-4-5
            if set(vals) == {14, 2, 3, 4, 5}:
                return True
            return False

        straight = is_straight(sorted_values)

        # === Hand Ranking (von hoch nach niedrig) ===
        if is_flush and straight:
            if max(values) == 14:  # A K Q J 10
                return PokerHand(cards, 9, "Royal Flush")
            else:
                return PokerHand(cards, 8, "Straight Flush")

        # Four of a Kind
        if 4 in rank_count.values():
            return PokerHand(cards, 7, "Four of a Kind")

        # Full House
        if 3 in rank_count.values() and 2 in rank_count.values():
            return PokerHand(cards, 6, "Full House")

        # Flush
        if is_flush:
            return PokerHand(cards, 5, "Flush")

        # Straight
        if straight:
            return PokerHand(cards, 4, "Straight")

        # Three of a Kind
        if 3 in rank_count.values():
            return PokerHand(cards, 3, "Three of a Kind")

        # Two Pair
        if list(rank_count.values()).count(2) == 2:
            return PokerHand(cards, 2, "Two Pair")

        # One Pair
        if 2 in rank_count.values():
            return PokerHand(cards, 1, "One Pair")

        # High Card
        high_rank = max(values)
        high_card_name = [k for k, v in rank_map.items() if v == high_rank][0]
        return PokerHand(cards, 0, f"High Card ({high_card_name})")

    # ====================== Game Management ======================

    def _new_game(self):
        self._game = {
            'chips': getattr(self._user_db_ent, 'poker_chips', self._chips_start),
            'pot': 0,
            'state': PokerState.IDLE,
            'player_hand': [],
            'dealer_hand': [],
            'current_bet': 0,
            'ante': 5,
        }
        if self._user_db_ent and not hasattr(self._user_db_ent, 'poker_chips'):
            self._user_db_ent.poker_chips = self._chips_start

    def _save_chips(self):
        if self._user_db_ent and self._game:
            self._user_db_ent.poker_chips = self._game['chips']

    # ====================== Öffentliche Commands ======================

    def cmd_poker(self):
        """Haupteingang: //POKER"""
        self._decode_param(defaults=['', 0, 0, 0, 0, 0])

        if not self._parameter or str(self._parameter[0]).upper() in ['HELP', 'H']:
            return self._show_help()

        if str(self._parameter[0]).upper() == 'HIGH':
            return self._show_highscore()

        if str(self._parameter[0]).upper() == 'HANDS':
            return self._show_hand_ranking()

        # Neues Spiel starten
        if not self._game or self._game['state'] == PokerState.IDLE:
            self._new_game()
            return self._start_new_round()

        # Spiel läuft bereits → Weiterleitung an In-Game Handler
        return self._handle_ingame_input()

    def _start_new_round(self):
        g = self._game
        g['pot'] = 0
        g['current_bet'] = 0

        # Ante
        ante = min(g['ante'], g['chips'])
        g['chips'] -= ante
        g['pot'] += ante

        # Karten austeilen
        deck = self._deck()
        random.shuffle(deck)
        g['player_hand'] = sorted(deck[:5], key=lambda x: (x[-1], x[:-1]))
        g['dealer_hand'] = deck[5:10]   # Dealer verdeckt

        g['state'] = PokerState.DEAL

        return self._show_table() + "\r\n" + self._get_action_prompt()

    def _show_table(self, show_dealer=False):
        g = self._game
        out = f"\r=== 5-Card Draw Poker ===\r"
        out += f"Chips: {g['chips']:>4}   Pot: {g['pot']:>4}   Ante: {g['ante']}\r\r"

        out += "Deine Hand:  " + self._hand_to_string(
            self._evaluate_hand(g['player_hand'])
        ) + "\r"

        if show_dealer:
            out += "Dealer Hand: " + self._hand_to_string(
                self._evaluate_hand(g['dealer_hand'])
            ) + "\r"

        return out

    def _get_action_prompt(self):
        state = self._game['state']
        if state in (PokerState.DEAL, PokerState.BET1):
            return "\rBET <anz> | CHECK | FOLD"
        elif state == PokerState.DRAW:
            return "\rDRAW <pos1> <pos2>... | DRAW (Auto) | HAND"
        else:
            return "\rBET <anz> | CALL | FOLD"

    def _handle_ingame_input(self):
        if not self._parameter[0]:
            return self._show_table() + self._get_action_prompt()

        cmd = str(self._parameter[0]).upper()
        args = self._parameter[1:]

        if cmd == 'FOLD':
            return self._end_round(lost=True)
        elif cmd in ('CHECK', 'CALL'):
            return self._process_bet(0)
        elif cmd == 'BET':
            try:
                amount = int(args[0]) if args else 10
                return self._process_bet(amount)
            except:
                return "\r # Ungültiger Betrag!\r"
        elif cmd == 'DRAW':
            return self._do_draw(args)
        elif cmd == 'HAND':
            return self._show_table()
        elif cmd in ('QUIT', 'END'):
            self._game = None
            return "\r # Poker beendet.\r"

        return "\r # Unbekannter Befehl. BET / DRAW / FOLD / HAND\r"

    def _process_bet(self, amount: int):
        g = self._game
        amount = max(0, min(amount, g['chips']))

        if g['state'] in (PokerState.DEAL, PokerState.BET1):
            g['chips'] -= amount
            g['pot'] += amount
            g['state'] = PokerState.DRAW
            return self._show_table() + "\r\nTauschphase:\rDRAW <Positionen> oder DRAW für Auto"

        # Zweite Wettrunde
        g['chips'] -= amount
        g['pot'] += amount
        return self._do_showdown()

    def _do_draw(self, positions):
        if not positions:
            # Auto-Draw: schlechteste Karten tauschen
            positions = [1, 2, 3]  # Dummy — kann später mit Hand-Evaluierung verbessert werden

        g = self._game
        deck = self._deck()
        random.shuffle(deck)

        # Einfaches Draw
        for pos in positions[:3]:  # max 3 Karten
            try:
                idx = int(pos) - 1
                if 0 <= idx < 5:
                    g['player_hand'][idx] = deck.pop()
            except:
                pass

        g['player_hand'].sort(key=lambda x: (x[-1], x[:-1]))
        g['state'] = PokerState.BET2

        return self._show_table() + "\r\nZweite Wettrunde:\rBET <anz> | CALL | FOLD"

    def _hand_to_string(self, hand: PokerHand):
        """Schöne Ausgabe der Hand"""
        cards_str = "  ".join(self._card_to_str(c) for c in hand.cards)
        return f"{cards_str}  →  {hand.rank_name}"

    def _do_showdown(self):
        g = self._game
        g['state'] = PokerState.SHOWDOWN

        player_eval = self._evaluate_hand(g['player_hand'])
        dealer_eval = self._evaluate_hand(g['dealer_hand'])

        out = self._show_table(show_dealer=True) + "\r\r"

        if player_eval.rank > dealer_eval.rank:
            win = g['pot']
            g['chips'] += win
            out += f"★★★ GEWONNEN! ★★★   +{win} Chips\r"
            out += f"Du hast: {player_eval.rank_name}\r"
        elif player_eval.rank == dealer_eval.rank:
            out += "Unentschieden!\r"
            g['chips'] += g['pot'] // 2
        else:
            out += f"Dealer gewinnt mit {dealer_eval.rank_name}.\r"

        self._save_chips()
        out += f"\rDein neuer Kontostand: {g['chips']} Chips\r"
        out += "\rEin neues Spiel starten mit //POKER\r"

        self._game = None
        return out

    def _end_round(self, lost=False):
        if lost:
            out = "\r # Du hast gefoldet.\r"
        else:
            out = "\r # Runde beendet.\r"
        self._game = None
        return out + "\rEin neues Spiel starten mit //POKER\r"

    @staticmethod
    def _show_help():
        return """\r
=== 5-Card Draw Poker ===
Befehle:
  //POKER          → Neues Spiel starten
  //POKER HIGH     → Highscore (später)
  //POKER HANDS    → Hand-Rangliste

Im Spiel:
  BET <zahl>   | CHECK | CALL | FOLD
  DRAW <1 3 5> | DRAW (Auto) | HAND
"""

    @staticmethod
    def _show_hand_ranking():
        return """\r
Poker Hand Rangliste:
9 Royal Flush
8 Straight Flush
7 Four of a Kind
6 Full House
5 Flush
4 Straight
3 Three of a Kind
2 Two Pair
1 One Pair
0 High Card
"""

    @staticmethod
    def _show_highscore():
        # Kann später aus UserDB erweitert werden
        return "\r # Highscore noch nicht implementiert.\r"