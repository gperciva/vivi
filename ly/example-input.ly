\version "2.16.0"

\include "vivi.ly"

tiny = \relative c' {
  \set Staff.instrumentName = "violin-1"
  %\tempo 4 = 120
  \tempo 4 = 96
  %\tempo 4 = 60
  %\key g \major
  %g4\f a b c

  g4\pp( d' a' e') | e( a, d, g,)

  %d4 e fis g
  %a'4 b c d
  %b1
  %e'8 d g b,
  %g16\f g g g g g g g g g g g g g g g


  %a4 \glissando c \glissando d^"IV" \glissando a    % glissando
  %a8\f d b d c d d_"IV" d   % hill climbing


  %d16\f a' e a fis a g a
  %d8 fis a cis d b g e
  %e8 a fis a g a a^"III" a
  %b'8\f e cis e d e e_"II" e

  %a'16\f e' b e c e d e
  %e'8\f f g a b a g f

  %g1\p\< ~ g1\f\>
  %d'1\p\< ~ d2...\f\> ~ d16\p
}

celloc = \relative c, {
  \set Staff.instrumentName = "cello-1"
  \tempo 4 = 60
  \clef bass
  \numericTimeSignature
  %c4\f <d g> <e g> f
  c4\f d e f
  %g a b c
  %c4\f c c c
  %g a b c
  %a4 \glissando c \glissando a \glissando c
  %b1
  %e'8 d g b,
}



one = \relative c' {
  \set Staff.instrumentName = "violin-1"
  \tempo 4 = 120
%  r4 a8
%  g4 a b c
  d4\mf e fis g
  %e'16\f e e e d d d d c c b b a4

%  c2..\p\< d8\f
%  d4\f\> e fis g\p
%  c4\p\< d e fis\f

%  g8\p r d' r a' r e' r
%  g,,8 d' a' e' e a, d, g,
%  c8 ~ c d ~ d e4 f
%  g'4^"pizz" f e^"arco" d
%  g'4^"pizz" f e^"arco" d
}

two = \relative c' {
  \set Staff.instrumentName = "violin-2"
  \tempo 4 = 120
  %g4(\mf b) c( cis)
  d4\mf^"pizz." e fis g
}

three = \relative c' {
  \set Staff.instrumentName = "viola-1"
  \tempo 4 = 120
  \clef alto
  d4\mp a' d, a'
}

four = \relative c, {
  \set Staff.instrumentName = "cello-1"
  \tempo 4 = 120
  \clef bass
  c2\f e
  %d'16 e f g a bes c d c bes a g f e d
}

\score {
  <<
    %\new Staff \celloc
    \new Staff \tiny
    %\new Staff \one
    %\new Staff \two
%    \new Staff \three
%    \new Staff \four
  >>
}
