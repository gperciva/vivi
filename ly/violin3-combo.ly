\version "2.16.0"
%\include "global.ly"
%%% dolce, espr, legato
dolce  = \markup{\italic dolce}
espr   = \markup{\italic espr.}
legato = \markup{\italic legato}




\header {
  title = "Three for Three"
  composer = "Graham Percival"
  piece = \markup{ \column {
		\line { \larger { Molto Vivace }}
		\line {Viola two begins when violin one reaches \hspace #0.5 \raise #0.5 \musicglyph #"scripts.segno" \hspace #-0.5 .  Viola three begins when violin two reaches \hspace #0.5 \raise #0.5 \musicglyph #"scripts.segno"\hspace #-0.5 .}
	\line {Viola two ends at \hspace #1 \raise #0.5
\musicglyph #"scripts.ulongfermata" and violin three ends at
\hspace #1 \raise #0.5 \musicglyph #"scripts.uverylongfermata" .}
	\line {In 3+3+2 and 2+3+3 meters, the 3-beats are strong and the 2-beat is weak.}
}}

	tagline = ""
	copyright = ""
}
\layout{
	ragged-bottom-last = ##f
  \context { \Score
    \override MetronomeMark #'extra-offset = #'(-12 . 0)
  }
}

#(define (compound-time grob one two a b c)
;;  (interpret-markup
;;   (ly:grob-layout grob)
;;   '(((baseline-skip . 2)
;;      (word-space . 1.6)
;;      (font-family . number)))
   (markup
    #:override '(baseline-skip . 0) #:number
    #:line (#:column (one two) #:hspace -0.5
      #:lower 1 #:line (#:text "(" #:hspace -2.5 #:small #:line (a "+" b "+" c) #:text ")" ))))

beaming = {
  % FIXME
  %#(override-auto-beam-setting '(end * * 8 8) 3 8)
  %#(override-auto-beam-setting '(end * * 8 8) 6 8)
  %#(override-auto-beam-setting '(end * * 8 8) 8 8)

  %#(override-auto-beam-setting '(end * * 3 4) 2 8)
  %#(override-auto-beam-setting '(end * * 3 4) 4 8)
%
%  #(override-auto-beam-setting '(end * * 4 4) 1 4)
%  #(override-auto-beam-setting '(end * * 4 4) 3 4)

  %#(override-auto-beam-setting '(end * * 7 8) 2 8)
  %#(override-auto-beam-setting '(end * * 7 8) 4 8)
  %#(override-auto-beam-setting '(end * * 7 8) 7 8)
}

global = {
	\beaming
  \clef treble
	\key a \minor
	\override Staff.TimeSignature #'style = #'numbered
	\override Score.MetronomeMark #'padding = #2.0
  \set Score.markFormatter = #format-mark-box-letters
	\tempo 4=166
  \time 8/8
  \once \override Staff.TimeSignature #'stencil
    = #(lambda (grob) (compound-time grob "8" "8" "3" "3" "2"))
	\repeat unfold 2 {
		\time 8/8
		s1*3
		\time 4/4
		s1
		\time 8/8
		s1*2
		\time 9/8
		s4.*3
		\time 3/4
		s2.
%		\break
		\mark \default
	}
	\repeat unfold 15 {
		s1*3
		s1
		s1*2
		s4.*3
		s2.
%		\break
		\mark \default
	}
}

violin = \transpose c' g' \relative c' {
	\beaming
	\time 8/8
  a4\f---. e'8---. a4---. a8 b c
	d4---. c8---. b4---. b8 a g
	a4---. g8---. e4---. e8 f g
	\time 2/2
	f8--\< e-- d-- f-- e-- d-- c-- g--
	\time 8/8
	a4\f---. e'8---. a4---. a8 b c
	d4---. e8---. f4---. f8 e d
	\time 9/8
	e8---. d---. c---. b---. c---. d---. c---. b---.\upbow g---.\upbow
	\time 3/4
	a8---.\< g---. e---. d---. c---. b---.

	\time 8/8
	c4---.\!\segno b8---.\mf a4---. c8 d e
	f4---. e8---. d4---. e8 f g
	a4---. b8---. c4---. b8 a b
	\time 2/2
	a8--\< b-- c-- a-- b-- c-- d-- f--
	\time 8/8
	e4---.\mf d8---. c4---. e8 d c
	b4---. a8---. g4---. g8 a b
	\time 9/8
	c8---. b---. a---. b---. a---. g---. a---. g---.\upbow e---.\upbow
	\time 3/4
	d8---. e---. d---.\> b---. a---. g---.
	
	\time 8/8
	a4.---.\p e---. g4---.
	f4.---. d---. e4---.
	c4.---. e---. g4---.
	\time 4/4
	f4( a) b-- d--
	\time 8/8
	c4.---. a---. c4---.
	b4.---. d---. f4---.
	\time 9/8
	e4.---. b---. c---.
	\time 3/4
	d4--\< e-- g--

	\time 8/8
	a8\f b c a4. b4
	c8 d e d4. ~ d4
	c8 b g a4. e4
	\time 4/4
	f2 e4 b
	\time 8/8
	c8\upbow d e f4. e4
	f8 g a b4. ~ b4
	\time 9/8
	c4.---. d---. e---.
	\time 3/4
	f4--\> e-- d--

	\time 8/8
	c4.\!\mp ~ c b8 a
	b4. ~ b c8 d
	e4. ~ e f8 e
	\time 4/4
	d8 c b2.
	\time 8/8
	a4. ~ a b8 g
	f4. ~ f ~ f4
	\time 9/8
	g4.---.-> g---.-> g---.->
	\time 3/4
	g,2.->

	\time 4/2
	c2\mf\downbow e
	d b
	c( e)
	d f
	e( c)
	b( g)
	\time 15/8
	b2.\upbow ~ b2. ~ b4.

	\time 4/2
	g1\p\downbow\open ~ g g^4 f
	c1 ~ c
	\time 6/8
	d4.\< d'
	\time 9/8
	d'2.->\> ~ d4.

	\time 4/2
	c1\!\mp b
	c aes--->
	g1 ~ g
	\time 6/8
	f2.
	\time 9/8
	g2.\upbow f4.\upbow

	\time 4/2
	\key c \minor
	ees2\mf c d f
	ees g b---> d
	ees4 d c2 ~ c d4 ees
	\time 6/8
	f4.\< aes
	\time 9/8
	g4. f g

	\time 8/4
  \once \override Staff.TimeSignature #'stencil
    = #(lambda (grob) (compound-time grob "8" "4" "2" "3" "3"))
  #(override-auto-beam-setting '(end 1 8 8 4) 2 4)
  #(override-auto-beam-setting '(end 1 8 8 4) 5 4)
  #(override-auto-beam-setting '(end 1 8 8 4) 8 4) 
	g4\f f g2. aes
	g4 f ees2. d
	c4 b aes2. g
	\time 6/8
	aes4.(\> d,)
	\time 9/8
	ees4. c b

	\time 8/4
	c2\mf g2. b4 c d
	ees2 c2. b4 aes g
	f2 ees2. f4 g ees
	\time 6/8
	d4.( f)
	\time 9/8
	aes2. d4.

	\time 8/4
	ees4\mp( f g4) f( ees) f2.
	g4( f g4) aes( c) b2.
	c4( d ees4) d( ees) g2.
	\time 6/8
	f4. g8( f g)
	\time 9/8
	aes2.\upbow g4.\upbow

	\time 4/4
	g2\mp f4 g
	aes1
	g2 g4 f
	d1
	c2 c4( b)
	c2 d4( ees)
	\time 8/8
	d8( c d) ees4. f4
	\time 7/8
	ees4 c d4.\>

	\time 4/4
	bes1\p\downbow
	b2( d)
	c1
	aes ~
	<aes>
	g1
	\time 8/8
	aes4.( g4.) d4
	\time 7/8
	ees4 f d4.

	\time 8/8
	ees8\f f g f4. ees4
	g8 aes g f4. ~ f4
	g8 aes a bes4. d4
	c4. f, d8 f
	ees8 d c d4. ees4
	d8 c bes aes4. ~ aes4
	f8 g aes c4.( bes4)
	\time 7/8
	g4 g b4.

	\time 8/8
	g8\mf g bes! c4. ~ c4
	d8 d b g4. ~ g4
	c8 aes ees f4. ~ f4
	aes4.( d) aes4
	aes8 aes g f4. ~ f4
	d8 d ees c4. ~ c4
	d4. d f4
	\time 7/8
	ees4 bes' f'4.

	\time 8/8
	c'4.\f aes8( bes) c bes aes
	g4. f8( g) f ees f
	g4. bes8( aes) g aes bes
	c8 d ees d ees f g( f)
	ees4. d8( c) aes bes c
	d4. c8( d) ees f g
	aes8( g) d ees( d) c d c
	\time 7/8
	bes8( aes) bes( aes) b( c) d

	\time 8/8
	ees4.\mp ees8( d) ees f ees
	d4. c8( bes) aes g d'
	c4. d,8( ees) f ees d
	ees8 f g f g aes g( bes)
	aes4. aes8( g) f aes g
	f4. ees8( f) ees d c
	aes8( bes) c bes( aes) g bes4
	\time 7/8
	ees4 ees d8( ees f)
}

lasttwo = \transpose c' g' \relative c'' {
	\beaming
	\time 8/8
	g4---.\p\verylongfermata f8---. g4---. g8 c,4
	d4---. ees8---. f4---. f8 ees4
	ees4---. f8---. g4---. g8 d'4
	\time 2/2
	c4( bes)\< c-- d--
	\time 8/8
	ees4---.\!\mf d8---. ees4---. ees8 c4
	bes4---. aes8---. c4---. c8 bes4
	\time 9/8
	bes4.---.\< g---. ees---.
	\time 3/4
	c4---> aes---> g--->\!
%zz
%		\break
%		\mark \default
}

lastone = \transpose c' g' \relative c {
	\beaming
	\time 8/8
	c4---.\f\longfermata g'8---. c4---. c8 d ees
	f4---. ees8---. d4---. d8 c bes
	c4---. bes8---. g4---. g8 aes bes
	\time 2/2
	aes8--\< g-- f-- aes-- g-- f-- g-- g--
	\time 8/8
	c,4---.\f g'8---. c4---. c8 d ees
	f4---. g8---. aes4---. aes8 g f
	\time 9/8
	g8---. f---. ees---. d---. ees---. f---. ees---. d---.\upbow bes---.\upbow
	\time 3/4
	c8---. d---. ees---. g---. c---. d---.
%	c8 bes g f ees d
	\time 1/1
	ees1\fermata
	\bar "|."
}



\score { \new StaffGroup <<
		\new Staff { <<
\set Staff.instrumentName = #"violin-1"
\set Staff.midiInstrument = #"violin"
\global \violin 
>> \lasttwo \lastone }
		\new Staff { <<
\set Staff.instrumentName = #"violin-2"
\set Staff.midiInstrument = #"violin"
\global {
  r1 r1 r1 r1 r1 r1 r4. r r
  \violin }
>> \lasttwo \time 1/1 g1 \bar "|." }
		\new Staff { <<
\set Staff.instrumentName = #"violin-3"
\set Staff.midiInstrument = #"cello"
\global {
  r1 r1 r1 r1 r1 r1 r4. r r
  r1 r1 r1 r1 r1 r1 r4. r r
  \violin}
>> \time 1/1 d'1 \bar "|." }
	>>
	\layout{
%		ragged-last=##t
		\context { \Score
			  \remove "Timing_translator"
  			\remove "Default_bar_line_engraver"
		}
		\context { \Staff
				\consists "Timing_translator"
				\consists "Default_bar_line_engraver"
		}
	}
	\midi{
    \context { \Score
			tempoWholesPerMinute = #(ly:make-moment 166 4)
%			tempoWholesPerMinute = #(ly:make-moment 130 4)
    }
  \context {
    \Voice
    \remove "Dynamic_performer"
%    \remove "Span_dynamic_performer"
  }
	}
}

