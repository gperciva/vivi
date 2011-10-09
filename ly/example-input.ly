\version "2.14.0"

\include "vivi.ly"

one = \relative c' {
  \set Staff.instrumentName = "violin-1"
  \tempo 4 = 120
%  r4 a8
%  g4 a b c
%  d e fis g
  e'4 d c8 b a4

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
  g4( b) c d
}

\score {
  <<
    \new Staff \one
    \new Staff \two
  >>
}
