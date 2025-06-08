// Lógica avançada de decisão de guerra
const AIWarDecisions = (function() {
  const WAR_SCORE_THRESHOLD = 0.65;
  
  function evaluateTarget(civilization, target) {
    // Fatores de avaliação
    const militaryScore = calculateMilitaryAdvantage(civilization, target);
    const economicScore = calculateEconomicAdvantage(civilization, target);
    const geographicScore = calculateGeographicAdvantage(civilization, target);
    const diplomaticScore = calculateDiplomaticFactors(civilization, target);
    
    const totalScore = 
      militaryScore * AI.params.militaryWeight +
      economicScore * AI.params.economicWeight +
      geographicScore * AI.params.geographicWeight;
    
    return totalScore * diplomaticScore;
  }
  
  function calculateMilitaryAdvantage(us, them) {
    const ourPower = us.militaryStrength;
    const theirPower = them.militaryStrength;
    
    // Considerar unidades próximas às fronteiras
    const borderPowerRatio = calculateBorderPowerRatio(us, them);
    
    // Considerar defesas de cidade
    const cityDefenseScore = them.cities.filter(city => 
      city.defenseStrength > AI.params.cityDefenseThreshold * ourPower
    ).length / them.cities.length;
    
    return (ourPower / (theirPower + 0.1)) * borderPowerRatio * (1 - cityDefenseScore);
  }
  
  function calculateBorderPowerRatio(us, them) {
    const borderTiles = getSharedBorderTiles(us, them);
    const ourBorderPower = calculatePowerInRegion(us, borderTiles);
    const theirBorderPower = calculatePowerInRegion(them, borderTiles);
    
    return (ourBorderPower + 0.5) / (theirBorderPower + 0.5) * AI.params.borderTensionMultiplier;
  }
  
  function calculateEconomicAdvantage(us, them) {
    return (us.goldPerTurn + us.productionTotal) / 
           (them.goldPerTurn + them.productionTotal + 1);
  }
  
  function calculateGeographicAdvantage(us, them) {
    // Priorizar alvos mais próximos
    const distance = calculateCapitalDistance(us, them);
    const distanceScore = 1 / (1 + distance * 0.1);
    
    // Considerar terreno favorável
    const terrainScore = calculateTerrainAdvantage(us, them);
    
    return distanceScore * terrainScore;
  }
  
  function calculateDiplomaticFactors(us, them) {
    // Evitar atacar aliados fortes
    if (us.getRelationWith(them) > AI.params.allyEvaluationThreshold) {
      return 0.3; // Reduz significativamente a chance
    }
    
    // Penalizar se alvo tiver muitos aliados
    const allyCount = them.getAllies().length;
    return 1 / (1 + allyCount * 0.2);
  }
  
  return {
    shouldDeclareWar: function(civilization, target) {
      if (civilization.wars.length >= AI.params.maxSimultaneousWars) return false;
      if (civilization.lastWarTurn > game.turn - AI.params.warCooldown) return false;
      
      const score = evaluateTarget(civilization, target);
      return score > WAR_SCORE_THRESHOLD && 
             score > (civilization.militaryStrength / target.militaryStrength) * AI.params.minPowerRatioForWar;
    }
  };
})();

// Injeta nova lógica na IA
AI.declareWarDecision = function(civilization, potentialTargets) {
  const validTargets = potentialTargets.filter(target => 
    AIWarDecisions.shouldDeclareWar(civilization, target)
  );
  
  if (validTargets.length > 0) {
    // Seleciona o alvo com maior pontuação
    const bestTarget = validTargets.reduce((best, current) => 
      evaluateTarget(civilization, current) > evaluateTarget(civilization, best) ? current : best
    );
    
    civilization.declareWar(bestTarget);
    return true;
  }
  return false;
};
