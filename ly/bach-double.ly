\version "2.16.0"

%\include "vivi.ly"
\pointAndClickOff



#(set-global-staff-size 16)

one = \relative c' {
  \set Staff.instrumentName = "violin-1"
  \set Staff.midiInstrument = "violin"
  \tempo 4 = 88
    r1 |
    r1 |
    r1 |
    r1 |
    a'16\f b c d e8-. a-. gis-. e-. b-. d-. |
    cis-. a-. g'!4. fis16 e fis8-.\upbow d-.\upbow |
    b-. d-. f-. a,-. gis-. e'-. a,-. d-. |
    c4 b-\trill a16 gis\> a b c d e f |
    %9
    g8-.\mf g,-. g'4 ~ g8-. e-.\> a,-. g'-.|

    f16\mp\> e d e f e d g a2\p ~ |
    a16 g fis e fis d e fis g2 ~ |
    g16 f e f g a bes g a\< bes a g f e d cis |
    d8-.\mf d'4 cis8-. d4 r8 f,-.\mp |
    e-. a-. a,4 ~ a8 d16 e fis g a fis |
    g8-. d16 c d b c d g,8-. c-. g'4 ~ |
    g8 fis16 g a8-. c, ~ c bes16\< c d8-. a'\mf ~ |
    a g ~ g f ~ f e16 d cis d b cis |

% bad default dynamic
    %18
    d\mf e f g a8-. d-. cis-. a-. e-. g-. |
    fis-. d-. c'!4. b16 a b8-. g-. |
    e-. g-. bes!-. d,-. cis-. a'-. d,-. g-. |
    f4 e-\trill d8-. c!16 bes! a g f e |
    f8-. a'-. e,-. g'-. d,16 g' f e d c bes a |
    bes8-. d'-. a,-. c'-. g,16 c' bes a g f e d |
    e bes' a g a e d cis d a' g f g d cis! b |
    cis g' f e f e d f e d cis! b a4 ~ |
    a16 f d f g e cis e f8-. d-. d'4 ~ |
    d16 bes g bes c a fis a bes8-. g-. bes'4 ~ |
    bes16 g, f e f8-. a' ~ a16 f, e d e8-. g' ~ |
    g16 e, d cis d8-. d' ~ d16 f e d e g f e |
    f a, b cis d e f d g, d' f8 ~ f16 d b! g |
    e' g, a b c d e c f, c' es8 ~ es16 c a f |
    %32
    d'8-. f-. g-. d-. e-. g-. a-. e-. |
    f16 g f e d c bes a g a' g f e d c bes |
    a8-. f'16 g a8-. f, ~ f16 e d c b8-. b' ~ |
    b e16 f g8-. e, ~ e16 d cis b a8-. a' ~ |
    a16 d f a d a f d a c e a c a e c |
    a b d f b f d a gis b d e b'8 r |
    r1 |
    r1 |
    r1 |
    r2 r4 r16 d,, c b |
    c8-. e'-. b,-. d'-. a,16 d' c b a g f e |
    f8-. a'-. e,-. g'-. d,16 g' f e d c b a |
    b f' e d e b a gis a e' d c d a gis! fis |
    gis d' c b c b a c b a gis! fis e8 r |
    %47
    a16 b c d e8-. a-. gis-. e-. b-. d-. |
    cis-. a-. g'!4 ~ g8 fis16 e fis8-. d-. |
    b-. d-. f!-. a,-. gis-. e'-. a,-. d-. |
    c4 b-\trill a r16 f e d |
    c8-. a'-. d,-. b'-. c,-. a'-. b,-. gis'-. c,-. a'-. e-. b'-. c-. a-. r16 g' f e |
    d( f )a d e,( g )a cis d a f d cis( e )g a |
    d,( f )a d e,( g )a cis d a f d d, e f d |
    e d e f e fis g e fis e fis g fis g a fis |
    g8-. d'-. r bes'-. a16 g fis e fis d e fis |
    g2 ~ g16 f! g a g bes a g |
    a2 ~ a16 g fis e d c bes a |
    %58
    bes8. c16 a8. g16 g g' fis e d c bes a |
    g( bes )d g a,( c )d fis g d bes g fis( a )c d |
    g,( bes )d g a,( c )d fis g d bes g g, as' g f |
    es8-. c'-. f,-. d'-. es,-. c'-. d,-. b'-. |
    es,-. c'-. g-. d'-. es-. c-. r16 g f g |
    a g a bes a bes c a bes a bes c d c d e |
    fis e fis g fis g a fis g c, bes a bes d g8 ~ |
    g a,-. g'4 ~ g8 a,-. d,-. f' ~ |
    f f,-. es'4 ~ es8 f,-. bes,-. d' |
    %67
    e,!16( f )g bes cis bes' a g f,( g )a cis d a' g f |
    g,( a )cis d e g f e a,( cis )d e f8-. d ~ |
    d g16 a bes8-. g, ~ g16 f e d c8-. c' ~ |
    c f16 g a8-. f, ~ f16 es d c bes8-. bes' ~ |
    bes16 c bes a g f e! d c d' c bes a g fis e |
    d8-. d'-. es-. bes-. c-. es-. f-. c-. |
    d16 f g a bes c d bes e,! bes' d8 ~ d16 bes g e |
    cis' e, f g a bes c a d, a' c8 ~ c16 a fis d |
    bes'8-. g-. d-. d' ~ d a16 f d4 ~ |
    d8-. bes-. g-. g' ~ g e16 cis a g f e |
    %77
    f8-. a'-. e,-. g'-. d,16 g' f e d c bes a |
    bes8-. d'-. a,-. c'-. g,16 c' bes a g f e d |
    e bes' a g a e d cis d a' g f g d cis b |
    cis g' f e f e d f e( d )cis b a4 ~ |
    a16 f d f g e cis e f8-. d-. d'4 ~ |
    d16 bes g bes c a fis a bes8-. g-. bes'4 ~ |
    bes16 g, f e f8-. a' ~ a16 f, e d e8-. g' ~ |
    g16 e, d cis d8-. d' ~ d16 f e d e g f e |
    f g f e d8-. d'-. cis-. a-. e-. g-. |
    fis-. d-. c'!4 ~ c8 b16 a b8-. g-. |
    e-. g-. bes!-. d,-. cis-. a'-. d,-. g-. |
    f4 e d2^\fermata |

}

two = \relative c' {
  \set Staff.instrumentName = "violin-2"
  \set Staff.midiInstrument = "violin"
  \tempo 4 = 88
    d16\f e f g a8-. d-. cis-. a-. e-. g-. |
    fis-. d-. c'!4. b16 a b8-.\upbow g-.\upbow |
    e-. g-. bes!-. d,-. cis-. a'-. d,-. g-. |
    f4 e-\trill d16\> cis d e fis gis a b |
    c\mp b a b c b c d e2 ~ |
    e16 d cis b cis( a) b cis d2 ~ |
    d16\< c! b c d e f d e f e d c b! a gis |
    a8\mf-. a'4 gis8-. a-. a,16\downbow\p gis a b c a |
    %9
    b\< a b c b cis d b cis! b cis d cis d e cis |

    d8-.\mf a'-. r f-. e16\> d cis b cis a b cis |
    d2\p ~ d16 c! d e d f! e d |
    e2 ~ e16 d cis b a g f e |
    d\< c'! bes a g f e g f8-.\mf d-. a'4 ~ |
    a16 b cis d e8-. g-. fis-. d-. a-. c-. |
    b-. g-. f'!4. e16 d e8-. c-. |
    a-. c-. es-. g,-. fis-. d'-. g,-. c-. |
    %17
    bes!4 a g r8 e-. |

% bad default dynamic
    a2\mf ~ a16 gis a b cis d e cis |
    d bes! a g a fis g a d,8-. g-. d'4 ~ |
    d8 cis16 d e f g8 ~ g16 e f g a8-. e ~ |
    e d4 cis8-. d4 r |
    r1 |
    r1 |
    r1 |
    r2 r4 r16 g,\mf f e |
    %26
    f8-. a'-. e,-. g'-. d,16 g' f e d c bes a |
    bes8-. d'-. a,-. c'-. g,16 c' bes a g f e d |
    e bes' a g a e d cis d a' g f g d cis! b |
    cis g' f e f e d f e d cis! b a4 ~ |
    a8-. d16 e f8-. d, ~ d16 c b a b8-. g' ~ |
    g c16 d e8-. c, ~ c16 bes! a g a8-. f'-. ~ |
    f16 g f e d c b a g a' g f e d cis b |
    a8-. [a'-. bes!-. f-.] g-. bes-. c-. g-. |
    a16 c d e f g a f b, f' a8 ~ a16 f d b |
    %35
    gis' b, c d e fis g e a, e' g8 ~ g16 e cis a |
    f'8-. [d-. a-. a'] ~ a e16 c a4 ~ |
    a8-. [f-. d-. d'] ~ d b16 gis e d c b |
    c8-. e'-. b,-. d'-. a,16 d' c b a g f e |
    f8-. a'-. e,-. g'-. d,16 g' f e d c b a |
    b f' e d e b a gis a e' d c d a gis! fis |
    gis d' c b c b a c b a gis! fis e4 ~
    e16 c a c d b gis b c8-. a-. a'4 ~ |
    a16 f d f g e cis e f8-. d-. f'4 ~ |
    f16 d, c b c8-. e' ~ e16 c, b e b8-. d' ~ |
    d16 b, a gis a8-. a' ~ a16 c b a b d c b |
    %46
    c b a b c b c d e2 ~ |
    e16 d cis b cis a b cis d2 ~ |
    d16 c! b c d e f d e f e d c b a gis |
    a8-. a'4 gis8-. a g16 f e d c b |
    a( c )e a b,( d )e gis a e c a gis( b )d e |
    a,( c )e a b,( d )e gis a e c a a, [bes' a g!] |
    f8-. d'-. g,-. e'-. f,-. d'-. e,-. cis'-. |
    f,-. d'-. a-. e'-. f-. d-. r d ~ |
    d g, c4 ~ c8-. a-. d,-. c'-. |
    bes16 a g a bes a bes c d2 ~ |
    d16 c b a b g a b c2 ~ |
    %57
    c16 bes a bes c d es c d es d c bes a g fis |
    g8-. g'4 fis8-. g4 r16 es, d c |
    bes8-. g'-. c,-. a'-. bes,-. g'-. a,-. fis'-. |
    bes,-. g'-. d-. a'-. bes-. g-. r16 f' es d |
    c( es )g c d,( f )g b c g es c b( d )f g |
    c,( es )g c d,( f )g b c g es c c,8-. es' ~ |
    es f, es'4 ~ es8 f,-. bes,-. d' ~ |
    d d,-. c'4 ~ c8 d,-. g,16 bes a b |
    cis b cis d cis d e cis d cis d e f e f g |
    a g a bes a bes c a bes es, d c d f bes8 ~ |
    bes-. bes-. g-. e'! ~ e a,-. f-. d' ~ |
    d g,-. e-. cis'-. d4 ~ d16 c bes a |
    bes d, e fis g a bes g c, g' bes8 ~ bes16 g e c |
    a' c, d e f g as f bes, f' as8 ~ as16 f d bes |
    g'8-. [bes-. c-. g-.] a-. c-. d-. a-. |
    bes16( c )bes a g f es d c d' c bes a g f es |
    d8-. bes'16 c d8-. bes ~ bes16 a g f e!8-. e' ~
    e a,16 bes c8-. a ~ a16 g fis e d4 ~ |
    d16 g bes d g d bes g d( f )a d f d a f |
    d( e )g bes e bes g d cis( e )g a e'8 r |
    %77
    r1 |
    r1 |
    r1 |
    r2 r4 r16 g, f e |
    f8-. a'-. e,-. g'-. d,16 g' f e d c bes a |
    bes8-. d'-. a,-. c'-. g,16 c' bes a g f e d |
    e bes' a g a e d cis d a' g f g d cis! b |
    cis g' f e f e d f e d cis! b a8 r |
    r a-. d-. f-. e-. cis-. a4 ~ |
    a16 g fis e fis d e fis g2 ~ |
    g16 f! e f g a bes g a bes a g f e d cis |
    d8 d'4 cis8 d2^\fermata |

}

violinBB =  \relative c' {
  \set Staff.instrumentName = "violin-3"
  \set Staff.midiInstrument = "violin"
  \tempo 4 = 88

    r1 |
    r1 |
    r1 |
    r1 |
    a'16\mf b c d e8-. a-. gis-. e-. b-. d-. |
    cis-. a-. g'!4. fis16 e fis8-. d-. |
    b-. d-. f-. a,-. gis-. e'-. a,-. d-. |
    c4 b\trill a16 gis\> a b c d e f |
    %9
    g8-.\mp g,-. g'4 ~ g8 e\> a, g' |
    f16\p e d e f e d g a2 ~ |
    a16 g fis e fis d e fis g2\p ~ |
    g16 f e f g a bes g a bes a g f e d cis |
    d8\mp-. d'4 cis8-. d4 r8 f,\p-. |
    e-. a-. a,4 ~ a8 d16 e fis g a fis |
    g8-. d16 c d b c d g,8-. c-. g'4 ~ |
    g8 fis16 g a8-. c, ~ c bes16 c d8-. a' ~ |
    a g ~ g f ~ f e16 d cis d b cis |
    %18
    d e f g a8-. d-. cis-. a-. e-. g-. |
    fis-. d-. c'!4. b16 a b8-. g-. |
    e-. g-. bes!-. d,-. cis-. a'-. d,-. g-. |
    f4 e\trill d r |
    d8\p^"pizz." r cis r d r r4 |
    d8 r d r d r r4 |
    r1 |
    r |
    d8 r e r f r r4 |
    g8 r fis r g r r4 |
    r1 |
    r |
    d,16\mp^"arco" e f g a8-. d-. b-. g-. r4 |
    c,16 d e f g8-. c-. a-. f-. r4 |
    r1 |
    r |
    f16 g a bes c8-. f-. d-. b-. r4 |
    e,16 fis gis a b8-. e-. cis-. a-. r4 |
    r1 |
    r |
    a8\p^"pizz." r gis r a r r4 |
    a8 r a r a r r4 |
    r1 |
    r |
    a8 r b r c r r4 |
    d8 r cis r d r r4 |
    r1 |
    r |
    %47
    a16\mf^"arco" b c d e8-. a-. gis-. e-. b-. d-. |
    cis-. a-. g'!4 ~ g8 fis16 e fis8-. d-. |
    b-. d-. f!-. a,-. gis-. e'-. a,-. d-. |
    c4 b\trill a r |
    e1\p ~ |
    e2. r4 |
    a,1 ~ |
    a2. r8 d\mf |
    e16 d e f e fis g e fis e fis g fis g a fis |
    g8-. d'-. r bes'-. a16 g fis e fis d e fis |
    g2 ~ g16 f! g a g bes a g |
    a2 ~ a16 g fis e d c bes a |
    %58
    bes8. c16 a8. g16 g4 r |
    d1\p ~ |
    d2. r4 |
    g,1 ~ |
    g2. r4 |
    r8 c'16 bes c8 r r d16 es d8 r |
    r8 d16 e! fis8 r r g16 fis g8 r |
    r8 g16 f! g8 r r f16 e d8 r |
    r8 es16 d c8 r r bes16 a bes8 r |
    r8 g16 f e!8 r r f16 e d8 r |
    r8 e16 d cis8 a' f r r4 |
    g,16 a bes c! d8-. g-. e-. c-. r4 |
    r16 g a bes c8-. f-. d-. bes-. r4 |
    r1 |
    r |
    bes16 c d es f8-. bes8-. g-. e-. r4 |
    a,16 b cis d e8-. a-. fis-. d-. r4 |
    r1 |
    r |
    d'8^"pizz." r cis r d r r4 |
    d8 r d r d r r4 |
    r1 |
    r |
    d8 r e r f r r4 |
    g8 r fis r g r r4 |
    r1 |
    r |
    d16\mf^"arco" e f g a8-. d-. cis-. a-. e-. g-. |
    fis d c'!4 ~ c8 b16 a-. b8-. g-. |
    e-. g-. bes!-. d,-. cis-. a'-. d,-. g-. |
    f4 e d2^\fermata |
    \bar "|."
}

violinCB =  \relative c' {
  \set Staff.instrumentName = "violin-4"
  \set Staff.midiInstrument = "violin"
  \tempo 4 = 88
    
    d16\mf e f g a8-. d-. cis-. a-. e-. g-. |
    fis-. d-. c'!4. b16 a b8-. g-. |
    e-. g-. bes!-. d,-. cis-. a'-. d,-. g-. |
    f4 e\trill d16\> cis d e fis gis a b |
    c\p b a b c b c d e2 ~ |
    e16 d cis b cis( a) b cis d2 ~ |
    d16 c! b c d e f d e f e d c b! a gis |
    a8-. a'4 gis8-. a-. a,16 gis a b c a |
    %9
    b\< a b c b cis d b cis! b cis d cis d e cis |
    d8\mp-. a'-. r f-. e16\> d cis b cis a b cis |
    d2\p ~ d16 c! d e d f! e d |
    e2~ e16 d cis b a g f e |
    d\< c'! bes a g f e g f8\mp-. d-. a'4 ~ |
    a16 b cis d e8-. g-. fis-. d-. a-. c-. |
    b-. g-. f'!4. e16 d e8-. c-. |
    a-. c-. es-. g,-. fis-. d'-. g,-. c-. |
    %17
    bes!4 a g r8 e-. |
    a2 ~ a16 gis a b cis d e cis |
    d bes! a g a fis g a d,8-. g-. d'4 ~ |
    d8-. cis16 d e f g8 ~ g16 e f g a8-. e ~ |
    e d4 cis8-. d4 r |

    a8\p^"pizz." r a r a r r4 |
    g8 r a r bes r r4 |
    r1 |
    r |
    a8 r cis r d r r4 |
    d8 r d r d r r4 |
    r1 |
    r |
    d,16\mp^"arco" e f g a8-. d-. b-. g-. r4 |
    c,16 d e f g8-. c-. a-. f-. r4 |
    r1 |
    r |
    f16 g a bes c8-. f-. d-. b-. r4 |
    e,16 fis gis a b8-. e-. cis-. a-. r4 |
    r1 |
    r |
    e8\p^"pizz." r e r e r r4 |
    d8 r e r f r r4 |
    r1 |
    r |
    e8 r gis r a r r4 |
    a8 r a r a r r4 |
    r1 |
    r |
    r8 a16\mf^"arco" b c b c d e2 ~ |
    e16 d cis b cis a b cis d2 ~ |
    d16 c! b c d e f d e f e d c b a gis |
    a8-. a'4 gis8-. a4 r4 |
    e,1\p ~ |
    e2. r4 |
    a,1 ~ |
    a2 ~ a8 a'\mf-. d4 ~ |
    d8-. g, c4 ~ c8 a-. d,-. c'-. |
    bes16 a g a bes a bes c d2 ~ |
    d16 c b a b g a b c2 ~ |
    c16 bes! a bes c d es c d es d c bes a g fis |
    g8-. g'4 fis8-. g4 r4 |
    d,1\p ~ |
    d2. r4 |
    g,1 ~ |
    g2. r4 |
    r8 a'16 g a8 r r bes16 a bes8 r |
    r a16 bes c8 r r bes16 c d8 r |
    r es16 d es8 r r a,16 g f8 r |
    r f16 g a8 r r f16 es d8 r |
    r g16 f e!8 r r f16 e d8 r |
    r e16 d cis8 e d r r4 |
    g,16 a bes c! d8-. g-. e-. c-. r4 |
    r16 g a bes c8-. f-. d-. bes-. r4 |
    r1 |
    r |
    bes16 c d es f8-. bes-. g-. e-. r4 |
    a,16 b cis d e8-. a-. fis-. d-. r4 |
    r1 |
    r |
    a'8^"pizz." r a r a r r4 |
    g8 r a r bes r r4 |
    r1 |
    r |
    a8 r cis r d r r4 |
    d8 r d r d r r4 |
    r1 |
    r |
    r8 a\mf^"arco"-. d-. f-. e-. cis-. a4 ~ |
    a16 g fis e fis d e fis g2 ~ |
    g16 f! e f g a bes g a bes a g f e d cis |
    d8-. d'4 cis8-. d2^\fermata |
    \bar "|."
}

violaB =  \relative c' {
  \set Staff.instrumentName = "viola-1"
  \set Staff.midiInstrument = "viola"
  \tempo 4 = 88
  \clef alto

    f4.\mf g8-. a-. e-. cis-. r |
    r fis16 g a8-. d,-. g16 fis g a g f e d |
    cis d e f g a bes g a8-. cis,-. d4 ~ |
    d cis d8-. a ~ a16 b c d |
    e8-. c-. a4 b8-. e-. gis4 |
    a8-. e[-. e'-. a,]-. r a-. a,-. d-. |
    r f-. b-. d-. r gis,-. e-. a-. |
    e-. f4 e16 d c8-. e[-. a-. a,]-. |
    e'4 r8-. e,-. a4 r8 cis-. |
    a'16 g f e d cis d e a,8-. e'-. g-. e-. |
    r a-. a,-. a'-. r d,-. g-. b,-. |
    c-. cis4 d8-. e-. e,-. f-. bes!-. |
    a-. f'-. bes-. g-. a16 g f e d e f g |
    a8-. e-. r a-. d,-. fis-. g-. fis-. |
    d-. g-. r d ~ d16 g, a b c d es f |
    es d c bes! a bes c a a' g fis e d c bes a |
    bes d cis d e8-. d ~ d e16 f g a g a |
    f8-. a,-. d-. f-. e-. cis-. e-. cis-. |
    a-. d-. r a' ~ a16 d, e f g a bes! c |
    bes a bes a g8-. g,-. e'16 cis d e f g a8-. |
    a,-. d-. bes'-. a-. f4 r |
    
    d8\p^"pizz." r e r f r r4 |
    bes,8 r fis' r g r r4 |
    r1 |
    r |
    f8 r a r a r r4 |
    g8 r a r bes r r4 |
    r1 |
    r |
    d,16\mp^"arco" e f g a8-. d-. b-. g-. r4 |
    c,16 d e f g8-. c-. a-. f-. r4 |
    r1 |
    r |
    f16 g a bes c8-. f,-. d'-. b-. r4 |
    e,16 fis gis a b8-. e-. cis-. a-. r4 |
    r1 |
    r |
    a,8\p^"pizz." r b r c r r4 |
    f8 r cis r d r r4 |
    r1 |
    r |
    c8 r e r e r r4 |
    d8 r e r f r r4 |
    r1 |
    r |

    e8\mf^"arco"-. c-. a4 b8-. e-. gis4 |
    a8-. e-. e'-. a,-. r a-. a,-. d-. |
    r f-. b,-. d-. r gis,-. e-. a-. |
    e'-. f4 e16 d c4 r |
    e1\p ~ |
    e2. r4 |
    a,1 ~ |
    a2. r8 a\mf-. |
    a4 r8 a-. d4 r8 fis-. |
    d'16 c bes a g fis g a d,8-. a'-. c-. a-. |
    r d-. d,-. d'-. r g,-. c-. e,-. |
    f-. fis4 g8-. a-. a,-. bes-. c-. |
    d-. es-. a,-. d-. bes4 r |
    d1\p ~ |
    d2. r4 |
    g,1 ~ |
    g2. r4 |
    r8 es'16 d c8 r r f16 es f8 r |
    r fis16 e d8 r r d16 c bes8 r |
    r a'8 e r r d16 cis d8 r |
    r c16 d es8 r r d16 es f8 r |
    r g16 f e!8 r r f16 e d8 r |
    r e16 d cis8 cis a' r r4 |
    g,16 a bes c! d8-. g-. e-. c-. r4 |
    f,16 g a bes c8-. f-. d-. bes-. r4 |
    r1 |
    r |
    bes16 c d es f8-. bes-. g-. e!-. r4 |
    a,16 b cis d e8-. a-. fis-. d-. r4 |
    r1 |
    r |
    d8^"pizz." r e r f r r4 |
    bes8 r fis r g r r4 |
    r1 |
    r |
    f8 r a r a r r4 |
    g8 r a r bes r r4 |
    r1 |
    r |
    a2\p\>^"arco" ~ a8 e\mf-. cis4 |
    d8-.  a[-. a'-. d,]-. r d'-. d,-. g-. |
    r bes-. e,-. g-. r cis,-. a-. d-. |
    a'-. bes4 a16 g fis2^\fermata |
    \bar "|."
}

continuo = \relative c {
  \set Staff.instrumentName = "cello-1"
  \set Staff.midiInstrument = "cello"
  \tempo 4 = 88
  \clef bass

    d8\mf-. d'-. c-. bes-. a16 g a bes a g f e |
    d\> c d es d c b a g2\p ~ |
    g2 ~ g8 f16 e f8-.\< bes-. |
    a-. g-. a-. a-. d,-.\mp [d'-.\> c-. b]-. |
    a-.\p a'-. g-. f-. e16 d e f e d c b |
    a gis a b a g f e d cis' d e d\< c b! a |
    gis4\mp r8 d' ~ d c16 b c8-. f-. |
    e-. d-. e-. e,-. a4 r |
    r1 |

    d16\mf\downbow e f g a8-. d-. cis-. a-. e-. g-. |
    fis-. d-. c'!4 ~ c8 b16 a b8-.\upbow g-.\upbow |
    e-. g-. bes-. d,-. cis-. a'-. d,-. g-. |
    f4\> e d16\mp cis d e f g a b |
    cis\> b a b cis a b cis d2\p ~ |
    d16 c! b a b g a b c2 ~ |
    c16 bes! a bes c d es c d es d c bes a g fis |
    g f! e d cis a d c! bes! d cis d e f g e |

    f e d e f e f g a2 ~ |
    a16 g fis e fis d e fis g2 ~ |
    g16 f! e f g a bes g a bes a g f e d cis |
    d8-. bes-. g-. a-. d,4 r |

    d'8-\mp^"pizz." r a r d, r r4 |
    g8 r d' r g r r4 |
    c8 r f, r bes r e, r |
    a r d, r a'\< e cis a |
    d8\mf r a r d, r r4 |
    g8 r d' r g r r4 |
    c8 r f, r bes r e, r |
    a r d, r a'\mp^"arco"-. e-. cis-. a-. |
    d8-. r r4 g8-. d-. b-. g-. |
    c-. r r4 f8-. c-. f,-. a-. |
    bes-. [d( b )g]-. c-. [e( cis )a]-. |
    d-. r r d,-. e-. r r e'-. |
    f-. r r d-. b-. b'16 c d8-. b-. |
    e,-. r r cis-. a-. a'16 b cis8-. a-. |
    d,-. r r d'-. c-. r r c,-. |
    f-. r r f,-. e-. r r4 |
    a'8\mp^"pizz." r e r a, r r4 |
    d8 r a r d, r r4 |
    g8 r c r f r b, r |
    e r a, r e'\< b gis e |
    a\mf r e' r a r r4 |
    d,8 r a r d, r r4 |
    g'8 r c, r f r b, r |
    e r a, r e' e,\mp\<-.^"arco" gis-. e-.] |
    %tutti
    a-.\mf a'-. g-. f-. e16 d e f e d cis b |
    a gis a b a g fis e d cis' d e d c b! a |
    gis4 r8 d'8 ~ d c16 b! c8-. f-. |
    e-. d-. e-. e,-. a-. [a'-.-\p gis-. e-.] |
    a-. r r4 r2 |
    r8 a-.\mp gis-. e-. a,-. [a'16 b c8-. cis]-. |
    d-. r r4 r2 |
    r8 d-. cis-. a-. d-. [d,-.-\mf f-. d-.] |
    a'4 r r2 |
    g,16 a bes c d8-. g-. fis-. d-. a-. c-. |
    b-. g-. f'4. e16[ d e8-. c]-. |
    a-. c-. es-. g,-. fis-. d'-. g,-. es'-. |
    d-. c-. d-. d,-. g-. g'-.-\p[ fis-. d-.] |

    g8 r r4 r2 |
    r8 g-.\mp fis-. d-. g,-. [g'16 a bes8 b] |
    c r r4 r2 |
    r8 c,-. b-. g-. c,-. [c'16 d es8 c] |
    f r r a,-. bes-. r r bes16 c |
    d8 r r d,-. g-. r r e |
    a r r a-. d-. r r d16 es |
    f8 r r f,-. bes-. r r bes'16 a |
    g8 r r e-. f-. r r d-. |
    e-. r r a,-. d-. a-. d,-. f-. |
    g r r4 c8-. g-. e-. c-. |
    f r r4 bes8-. [f'( d) bes]-. |
    es-. [g( e) c]-. f-. [a( fis) d]-. |
    g-. r r g,-. a-. r r a'-. |
    bes-. r r g-. e-. [e,16 f g8-. e]-. |
    a-. r r fis'-. d-. [d,16 e fis8-. d]-. |
    g-. r r g'-. f-. r r f,-. |
    bes-. r r bes'-. a-. r r4 |
    d,8^"pizz." r a r d, r r4 |
    g8 r d' r g r r4 |
    c8 r f, r bes r e, r |
    a r d, r a' e cis a |
    d8 r a r d, r r4 |
    g8 r d' r g r r4 |
    c,8 r f r bes, r e r |
    a, r d r a' [a,-\mf^"arco"-. cis-. a]-. |
    d16 cis d e f e f g a g a bes a g fis e |
    d c d es d c bes a g fis g a g f e! d |
    cis4 r8 g''\mf ~ g f16 e f8-. bes-. |
    a-. g-. a-. a,-. d,2-\fermata |

\bar "|."
}

\book{
\score {
  <<
    \new Staff \one
    \new Staff \two
    \new Staff \violinBB
    \new Staff \violinCB
    \new Staff \violaB
    \new Staff \continuo
  >>
  \layout{}
  \midi{}
}

\header {
    title = 	"Concerto in D minor"
    subtitle =	"for two violins and strings"
    composer =	"Johann Sebastian Bach (1685-1750)"
    opus =	"BWV 1043"
    enteredby = "David Chan"

    %mutopia headers
    mutopiatitle =      "Concerto in D minor for two violins and strings"
    mutopiacomposer =   "BachJS"
    mutopiaopus =       "BWV 1043"
    mutopiainstrument = "Violin Duet and String Orchestra: Two Violins, Viola, 'Cello"
    date =              "1717-23"
    source =            "Bach Gesellschaft zu Leipzig, 1874"
	% M200.a.13.23^3 in Cambridge University Library.
    style =             "Baroque"
    copyright =         "Public Domain"    

    maintainer =       "David Chan"
    maintainerEmail =  "davidchan@sheetmusic.org.uk"
    maintainerWeb =    "http://www.sheetmusic.org.uk/"
    moreInfo = "The maintainer has been unable to locate an out-of-copyright piano accompaniment.  If anyone would be willing to submit such an arrangement to Mutopia, the world will be very grateful."

 footer = "Mutopia-2013/01/06-3"
 tagline = \markup { \override #'(box-padding . 1.0) \override #'(baseline-skip . 2.7) \box \center-column { \small \line { Sheet music from \with-url #"http://www.MutopiaProject.org" \line { \concat { \teeny www. \normalsize MutopiaProject \teeny .org } \hspace #0.5 } • \hspace #0.5 \italic Free to download, with the \italic freedom to distribute, modify and perform. } \line { \small \line { Typeset using \with-url #"http://www.LilyPond.org" \line { \concat { \teeny www. \normalsize LilyPond \teeny .org }} by \concat { \maintainer . } \hspace #0.5 Reference: \footer } } \line { \teeny \line { This sheet music has been placed in the public domain by the typesetter, for details \concat { see: \hspace #0.3 \with-url #"http://creativecommons.org/licenses/publicdomain" http://creativecommons.org/licenses/publicdomain } } } } } 
}
}
