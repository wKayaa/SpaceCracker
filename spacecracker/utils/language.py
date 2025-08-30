#!/usr/bin/env python3
"""
Multi-Language Support Module
Provides English/French UI translations for SpaceCracker v3.1
"""

import json
import os
from typing import Dict, Any

class LanguageManager:
    """Manages multi-language support for the application"""
    
    def __init__(self, language: str = 'en'):
        self.language = language
        self.translations = self._load_translations()
        
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation dictionaries"""
        return {
            'en': {
                # CLI Messages
                'scan_starting': '🚀 Starting SpaceCracker scan...',
                'scan_completed': '✅ Scan completed!',
                'scan_interrupted': '⚠️  Scan interrupted by user',
                'scan_failed': '❌ Scan failed: {}',
                'targets_loaded': 'Loaded {} targets from file',
                'single_target': 'Single target: {}',
                'findings': 'Findings: {}',
                'errors': 'Errors: {}',
                'reports_saved': 'Reports saved to: {}',
                
                # Interactive Wizard
                'wizard_title': '🚀 SpaceCracker - Interactive Scan Wizard',
                'authorization_disclaimer': '⚠️  AUTHORIZATION DISCLAIMER',
                'authorization_warning': 'This tool should only be used on systems you own or have explicit permission to test.',
                'authorization_prompt': 'Do you have authorization to scan the target systems? [y/N]: ',
                'authorization_required': 'Authorization required. Exiting.',
                'step_target_config': '📋 Step 1: Target Configuration',
                'target_input_prompt': 'Enter target file path or single target URL: ',
                'step_module_selection': '🔧 Step 2: Module Selection',
                'available_modules': 'Available modules:',
                'module_selection_prompt': 'Select modules (enter numbers separated by commas, or \'all\' for all modules):',
                'choice_prompt': 'Choice: ',
                'invalid_selection': 'Invalid selection, using all modules',
                'selected_modules': 'Selected modules: {}',
                'step_performance': '⚡ Step 3: Performance Settings',
                'threads_prompt': 'Number of threads [50]: ',
                'rate_limit_prompt': 'Requests per second [10]: ',
                'step_telegram': '📱 Step 4: Telegram Notifications',
                'telegram_prompt': 'Enable Telegram notifications? [y/N]: ',
                'scan_plan_summary': '📊 Scan Plan Summary',
                'plan_targets': 'Targets: {}',
                'plan_modules': 'Modules: {}',
                'plan_threads': 'Threads: {}',
                'plan_rate_limit': 'Rate Limit: {} req/s',
                'plan_telegram': 'Telegram: {}',
                'telegram_enabled': 'Enabled',
                'telegram_disabled': 'Disabled',
                'proceed_prompt': 'Proceed with scan? [Y/n]: ',
                'scan_cancelled': 'Scan cancelled',
                
                # Performance Modes
                'performance_low': 'Low Performance',
                'performance_normal': 'Normal Performance', 
                'performance_high': 'High Performance',
                'performance_auto': 'Auto-Configuration',
                
                # Progress Display
                'scan_progress': 'SCAN IN PROGRESS',
                'elapsed_time': 'Elapsed time: {}',
                'progress': 'Progress: {}%',
                'total_stats': 'TOTAL STATS:',
                'urls_processed': 'URLs processed: {}',
                'unique_urls': 'Unique URLs: {}',
                'urls_validated': 'URLs validated: {}',
                'success_rate': 'Success rate: {}%',
                'hits_found': 'HITS FOUND (TOTAL: {})',
                'cpu_usage': 'CPU: {}%',
                'ram_usage': 'RAM: {} MB',
                'http_rate': 'HTTP: {}/s',
                
                # Module Names
                'laravel_scanner': 'Laravel Security Scanner',
                'smtp_scanner': 'SMTP Security Scanner',
                'js_scanner': 'JavaScript Scanner',
                'git_scanner': 'Git Scanner',
                'ggb_scanner': 'Generic Global Bucket Scanner',
                
                # Error Messages
                'error_loading_targets': 'Error loading targets from {}: {}',
                'error_targets_required': 'Error: --targets is required in non-interactive mode',
                'warning_failed_module': 'Warning: Failed to load module {}: {}',
                'warning_failed_discovery': 'Warning: Failed to discover modules: {}'
            },
            
            'fr': {
                # CLI Messages
                'scan_starting': '🚀 Démarrage du scan SpaceCracker...',
                'scan_completed': '✅ Scan terminé !',
                'scan_interrupted': '⚠️  Scan interrompu par l\'utilisateur',
                'scan_failed': '❌ Échec du scan : {}',
                'targets_loaded': '{} cibles chargées depuis le fichier',
                'single_target': 'Cible unique : {}',
                'findings': 'Découvertes : {}',
                'errors': 'Erreurs : {}',
                'reports_saved': 'Rapports sauvegardés dans : {}',
                
                # Interactive Wizard
                'wizard_title': '🚀 SpaceCracker - Assistant de Scan Interactif',
                'authorization_disclaimer': '⚠️  AVERTISSEMENT D\'AUTORISATION',
                'authorization_warning': 'Cet outil ne doit être utilisé que sur des systèmes que vous possédez ou pour lesquels vous avez une autorisation explicite.',
                'authorization_prompt': 'Avez-vous l\'autorisation de scanner les systèmes cibles ? [o/N] : ',
                'authorization_required': 'Autorisation requise. Sortie.',
                'step_target_config': '📋 Étape 1 : Configuration des Cibles',
                'target_input_prompt': 'Entrez le chemin du fichier de cibles ou une URL cible unique : ',
                'step_module_selection': '🔧 Étape 2 : Sélection des Modules',
                'available_modules': 'Modules disponibles :',
                'module_selection_prompt': 'Sélectionnez les modules (entrez les numéros séparés par des virgules, ou \'all\' pour tous) :',
                'choice_prompt': 'Choix : ',
                'invalid_selection': 'Sélection invalide, utilisation de tous les modules',
                'selected_modules': 'Modules sélectionnés : {}',
                'step_performance': '⚡ Étape 3 : Paramètres de Performance',
                'threads_prompt': 'Nombre de threads [50] : ',
                'rate_limit_prompt': 'Requêtes par seconde [10] : ',
                'step_telegram': '📱 Étape 4 : Notifications Telegram',
                'telegram_prompt': 'Activer les notifications Telegram ? [o/N] : ',
                'scan_plan_summary': '📊 Résumé du Plan de Scan',
                'plan_targets': 'Cibles : {}',
                'plan_modules': 'Modules : {}',
                'plan_threads': 'Threads : {}',
                'plan_rate_limit': 'Limite de débit : {} req/s',
                'plan_telegram': 'Telegram : {}',
                'telegram_enabled': 'Activé',
                'telegram_disabled': 'Désactivé',
                'proceed_prompt': 'Procéder au scan ? [O/n] : ',
                'scan_cancelled': 'Scan annulé',
                
                # Performance Modes
                'performance_low': 'Performance Faible',
                'performance_normal': 'Performance Normale',
                'performance_high': 'Haute Performance',
                'performance_auto': 'Configuration Automatique',
                
                # Progress Display  
                'scan_progress': 'SCAN EN COURS',
                'elapsed_time': 'Temps écoulé : {}',
                'progress': 'Progrès : {}%',
                'total_stats': 'STATISTIQUES TOTALES :',
                'urls_processed': 'URLs traitées : {}',
                'unique_urls': 'URLs uniques : {}',
                'urls_validated': 'URLs validées : {}',
                'success_rate': 'Taux de réussite : {}%',
                'hits_found': 'RÉSULTATS TROUVÉS (TOTAL : {})',
                'cpu_usage': 'CPU : {}%',
                'ram_usage': 'RAM : {} MB',
                'http_rate': 'HTTP : {}/s',
                
                # Module Names
                'laravel_scanner': 'Scanner de Sécurité Laravel',
                'smtp_scanner': 'Scanner de Sécurité SMTP',
                'js_scanner': 'Scanner JavaScript',
                'git_scanner': 'Scanner Git',
                'ggb_scanner': 'Scanner de Conteneurs Globaux Génériques',
                
                # Error Messages
                'error_loading_targets': 'Erreur lors du chargement des cibles depuis {} : {}',
                'error_targets_required': 'Erreur : --targets est requis en mode non-interactif',
                'warning_failed_module': 'Attention : Échec du chargement du module {} : {}',
                'warning_failed_discovery': 'Attention : Échec de la découverte des modules : {}'
            }
        }
    
    def get(self, key: str, *args, **kwargs) -> str:
        """Get translated string"""
        translation = self.translations.get(self.language, {}).get(key, key)
        
        # Handle string formatting
        if args:
            try:
                return translation.format(*args)
            except:
                return translation
        elif kwargs:
            try:
                return translation.format(**kwargs)
            except:
                return translation
        
        return translation
    
    def set_language(self, language: str):
        """Set the current language"""
        if language in self.translations:
            self.language = language
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return list(self.translations.keys())

# Global instance
_lang_manager = None

def init_language(language: str = 'en') -> LanguageManager:
    """Initialize global language manager"""
    global _lang_manager
    _lang_manager = LanguageManager(language)
    return _lang_manager

def get_language_manager() -> LanguageManager:
    """Get current language manager instance"""
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = LanguageManager()
    return _lang_manager

def _(key: str, *args, **kwargs) -> str:
    """Convenient translation function"""
    return get_language_manager().get(key, *args, **kwargs)