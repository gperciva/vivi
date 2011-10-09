\version "2.14.0"

\include "vivi.ly"

one = \relative c' {
  \set Staff.instrumentName = "violin-1"
  \set Staff.midiInstrument = "violin"
  \tempo 4 = 88
    r1 |
    r1 |
    r1 |
    r1 |
    a'16\f b c d e8 a gis e b d |
    cis a g'!4. fis16 e fis8 d |
    b d f a, gis e' a, d |
    c4 b-\trill a16 gis a b c d e f |
    %9
    g8 g, g'4 ~ g8 e a, g' |
%{
    f16 e d e f e d g a2 ~ |
    a16 g fis e fis d e fis g2 ~ |
    g16 f e f g a bes g a bes a g f e d cis |
    d8 d'4 cis8 d4 r8 f, |
    e a a,4 ~ a8 d16 e fis g a fis |
    g8 d16 c d b c d g,8 c g'4 ~ |
    g8 fis16 g a8 c, ~ c bes16 c d8 a' ~ |
    a g ~ g f ~ f e16 d cis d b cis |
%}
}

two = \relative c' {
  \set Staff.instrumentName = "violin-2"
  \set Staff.midiInstrument = "violin"
  \tempo 4 = 88
    d16\f e f g a8 d cis a e g |
    fis d c'!4. b16 a b8 g |
    e g bes! d, cis a' d, g |
    f4 e-\trill d16 cis d e fis gis a b |
    c\> b a b c b c d e2\mp ~ |
    e16 d cis b cis a b cis d2 ~ |
    d16\< c! b c d e f d e f e d c b! a gis |
    a8\f a'4 gis8 a a,16 gis a b c a |
    %9
    b a b c b cis d b cis! b cis d cis d e cis |
%{
    d8 a' r f e16 d cis b cis a b cis |
    d2 ~ d16 c! d e d f! e d |
    e2~ e16 d cis b a g f e |
    d c'! bes a g f e g f8 d a'4 ~ |
    a16 b cis d e8 g fis d a c |
    b g f'!4. e16 d e8 c |
    a c es g, fis d' g, c |
    %17
    bes!4 a g r8 e |
%}
}

\score {
  <<
    \new Staff \one
    \new Staff \two
  >>
  \layout{}
  \midi{}
}
