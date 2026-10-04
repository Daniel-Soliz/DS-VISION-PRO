from __future__ import annotations

PATTERN_CATALOG = [
    {"name": "MARTELO", "direction": "ALTA", "family": "Reversão", "description": "Pavio inferior longo após pressão vendedora; ganha força em suporte/LTA."},
    {"name": "MARTELO INVERTIDO", "direction": "ALTA", "family": "Reversão", "description": "Pavio superior longo após queda; precisa de confirmação compradora."},
    {"name": "ENGOLFO DE ALTA", "direction": "ALTA", "family": "Reversão", "description": "Corpo comprador envolve o corpo vendedor anterior."},
    {"name": "PIERCING LINE", "direction": "ALTA", "family": "Reversão", "description": "Recuperação compradora que fecha acima da metade da vela anterior."},
    {"name": "HARAMI DE ALTA", "direction": "ALTA", "family": "Reversão", "description": "Vela compradora menor contida no corpo vendedor anterior."},
    {"name": "MORNING STAR", "direction": "ALTA", "family": "3 velas", "description": "Sequência de exaustão da queda seguida por retomada compradora."},
    {"name": "3 SOLDADOS BRANCOS", "direction": "ALTA", "family": "Continuação", "description": "Três velas compradoras consistentes com avanço de fechamentos."},
    {"name": "MARUBOZU DE ALTA", "direction": "ALTA", "family": "Força", "description": "Corpo amplo e pouco pavio, indicando domínio comprador."},
    {"name": "TWEEZER BOTTOM", "direction": "ALTA", "family": "Reversão", "description": "Duas velas testam praticamente o mesmo fundo e rejeitam a região."},
    {"name": "BULLISH KICKER", "direction": "ALTA", "family": "Impulso", "description": "Mudança brusca de domínio vendedor para comprador."},
    {"name": "THREE INSIDE UP", "direction": "ALTA", "family": "3 velas", "description": "Harami de alta confirmado por fechamento comprador adicional."},
    {"name": "THREE OUTSIDE UP", "direction": "ALTA", "family": "3 velas", "description": "Engolfo de alta confirmado por continuidade compradora."},

    {"name": "ESTRELA CADENTE", "direction": "BAIXA", "family": "Reversão", "description": "Pavio superior longo após alta; ganha força em resistência/LTB."},
    {"name": "HOMEM ENFORCADO", "direction": "BAIXA", "family": "Reversão", "description": "Pavio inferior longo após alta; alerta de perda de força compradora."},
    {"name": "ENGOLFO DE BAIXA", "direction": "BAIXA", "family": "Reversão", "description": "Corpo vendedor envolve o corpo comprador anterior."},
    {"name": "DARK CLOUD COVER", "direction": "BAIXA", "family": "Reversão", "description": "Pressão vendedora fecha abaixo da metade da vela anterior."},
    {"name": "HARAMI DE BAIXA", "direction": "BAIXA", "family": "Reversão", "description": "Vela vendedora menor contida no corpo comprador anterior."},
    {"name": "EVENING STAR", "direction": "BAIXA", "family": "3 velas", "description": "Exaustão da alta seguida por retomada vendedora."},
    {"name": "3 CORVOS NEGROS", "direction": "BAIXA", "family": "Continuação", "description": "Três velas vendedoras consistentes com queda dos fechamentos."},
    {"name": "MARUBOZU DE BAIXA", "direction": "BAIXA", "family": "Força", "description": "Corpo amplo e pouco pavio, indicando domínio vendedor."},
    {"name": "TWEEZER TOP", "direction": "BAIXA", "family": "Reversão", "description": "Duas velas testam praticamente o mesmo topo e rejeitam a região."},
    {"name": "BEARISH KICKER", "direction": "BAIXA", "family": "Impulso", "description": "Mudança brusca de domínio comprador para vendedor."},
    {"name": "THREE INSIDE DOWN", "direction": "BAIXA", "family": "3 velas", "description": "Harami de baixa confirmado por fechamento vendedor adicional."},
    {"name": "THREE OUTSIDE DOWN", "direction": "BAIXA", "family": "3 velas", "description": "Engolfo de baixa confirmado por continuidade vendedora."},

    {"name": "DOJI", "direction": "NEUTRO", "family": "Indecisão", "description": "Abertura e fechamento próximos; exige contexto para decisão."},
    {"name": "DRAGONFLY DOJI", "direction": "ALTA", "family": "Rejeição", "description": "Forte rejeição inferior; mais relevante em suporte."},
    {"name": "GRAVESTONE DOJI", "direction": "BAIXA", "family": "Rejeição", "description": "Forte rejeição superior; mais relevante em resistência."},
    {"name": "SPINNING TOP", "direction": "NEUTRO", "family": "Indecisão", "description": "Corpo curto com pavios; mostra equilíbrio temporário."},
]
