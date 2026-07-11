#!/usr/bin/env python3
"""
Benchmark AI Council Pipeline.
Executes the LiveCouncil on a predefined set of prompts to measure performance,
success rate, and consensus quality.
"""

import asyncio
import csv
import json
import logging
import os
import time
import traceback
from datetime import datetime
from pathlib import Path
from collections import Counter

# Add parent directory to path to allow imports from src
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.council.live_council import LiveCouncil
from src.models.prompt_request import PromptRequest
from src.providers.provider_registry import ProviderRegistry
from src.council.council_executor import CouncilExecutor

# Configure basic logging
logging.basicConfig(level=logging.WARNING)

def normalize_learning_style(style: str) -> str:
    """
    Normalizes a friendly learning style name to a supported enum value.
    """
    mapping = {
        "visual learner": "visual",
        "step-by-step learner": "step_by_step",
        "hands-on learner": "step_by_step",
        "project-based learning": "step_by_step",
        "exam preparation": "exam_focused",
        "beginner learner": "conversational",
        "advanced learner": "research_oriented",
        "visual": "visual",
        "conversational": "conversational",
        "research": "research_oriented",
        "step_by_step": "step_by_step",
        "exam_focused": "exam_focused",
        "research_oriented": "research_oriented"
    }
    
    normalized = style.lower().strip()
    
    if normalized in mapping:
        return mapping[normalized]
        
    raise ValueError(f"Unknown learning style: '{style}'")


class BenchmarkRunner:
    def __init__(self, data_path: str, reports_dir: str):
        self.data_path = Path(data_path)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
        # Load env vars manually if dotenv is available, but the providers usually handle this.
        try:
            # Configure stdout to handle utf-8 characters on Windows
            if sys.stdout.encoding != 'utf-8' and hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
                
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
            
        self.council = LiveCouncil()

    def load_prompts(self):
        print("Loading benchmark dataset...")
        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} prompts")
        return data

    async def run_single_benchmark(self, prompt_data: dict, index: int, total: int):
        print(f"Running benchmark {index}/{total}...")
        print(f"Topic: {prompt_data.get('topic')}")
        print(f"Learning Style: {prompt_data.get('learning_style')}\n")

        try:
            normalized_style = normalize_learning_style(prompt_data["learning_style"])
        except ValueError as e:
            # Handle invalid style gracefully
            print(f"Error occurred: {str(e)}\n")
            print("-" * 32)
            run_result = {
                "topic": prompt_data["topic"],
                "learning_style": prompt_data["learning_style"],
                "execution_time": 0.0,
                "winning_provider": "error",
                "contributors": [],
                "prompt_score": 0.0,
                "consensus_score": 0.0,
                "classification": "error",
                "provider_stats": [],
                "num_successful_providers": 0,
                "error": str(e)
            }
            self.results.append(run_result)
            return run_result

        request = PromptRequest(
            user_id=1,
            topic=prompt_data["topic"],
            learning_style=normalized_style,
            difficulty=prompt_data["difficulty"],
            education_level=prompt_data["difficulty"],
            output_length="medium",
            objective=prompt_data["goal"]
        )
        
        start_time = time.time()
        
        try:
            print("Executing live council...")
            result = await self.council.execute(request, timeout=300.0)
            end_time = time.time()
            execution_time = end_time - start_time
            print("Council execution completed")
            
            # Extract data
            responses = result["responses"]
            consensus = result["consensus"]
            score = result["score"]
            contributors = result["contributors"]
            
            winning_provider = consensus.contributors[0] if consensus.contributors else "none"
            prompt_score = score.overall_score
            consensus_score = consensus.quality_score if consensus.quality_score is not None else 0.0
            classification = score.classification.value if hasattr(score.classification, "value") else str(score.classification)
            
            # Provider latencies & success
            provider_stats = []
            for r in responses:
                p_name = getattr(r, "provider_name", "unknown")
                provider_stats.append({
                    "provider_name": p_name,
                    "model_name": getattr(r, "model", "unknown"),
                    "success": True,
                    "latency": (r.metadata.response_time * 1000) if getattr(r, "metadata", None) and getattr(r.metadata, "response_time", None) else 0.0,
                    "response_length": len(r.prompt) if getattr(r, "prompt", None) else 0,
                    "error_message": None
                })
                
            failed_providers_list = result.get("failed_providers", [])
            error_details_dict = result.get("error_details", {})
            for p_name in failed_providers_list:
                err_detail = error_details_dict.get(p_name, "Unknown error")
                
                if isinstance(err_detail, dict):
                    status_str = err_detail.get("status_code", "N/A")
                    msg = err_detail.get("message", "Unknown")
                    err_type = err_detail.get("type", "Error")
                    
                    if status_str != "N/A":
                        error_message = f"{status_str} {err_type}: {msg}"
                    else:
                        error_message = f"{err_type}: {msg}"
                else:
                    error_message = str(err_detail)
                    
                provider_stats.append({
                    "provider_name": p_name,
                    "model_name": "unknown",
                    "success": False,
                    "latency": 0.0,
                    "response_length": 0,
                    "error_message": error_message
                })
                
            successful_providers = [p for p in provider_stats if p["success"]]
            
            confidence_score = consensus.confidence_score if consensus.confidence_score is not None else 0.0
            agreement_score = consensus.agreement_score if consensus.agreement_score is not None else 0.0
            completeness_score = consensus.completeness_score if consensus.completeness_score is not None else 0.0
            learning_style_score = consensus.learning_style_score if consensus.learning_style_score is not None else 0.0
            provider_contributions = consensus.provider_contributions if consensus.provider_contributions else {}
            
            # Phase 3 extraction
            diversity_score = consensus.diversity_score if consensus.diversity_score is not None else 0.0
            coverage_score = consensus.coverage_score if consensus.coverage_score is not None else 0.0
            learning_style_verification = consensus.learning_style_verification if consensus.learning_style_verification else {}
            explanation = consensus.explanation if consensus.explanation else ""
            evaluation_summary = consensus.evaluation_summary if consensus.evaluation_summary else ""
            confidence_level = consensus.confidence_level if consensus.confidence_level else "Unknown"
            conflicting_concepts = consensus.conflicting_concepts if consensus.conflicting_concepts else []
            # Phase 4 Production Metrics
            cache_hit = consensus.cache_hit if consensus.cache_hit is not None else False
            parallel_efficiency = consensus.parallel_efficiency if consensus.parallel_efficiency is not None else 1.0
            
            run_result = {
                "topic": prompt_data["topic"],
                "learning_style": prompt_data["learning_style"],
                "execution_time": execution_time,
                "winning_provider": winning_provider,
                "contributors": contributors,
                "prompt_score": prompt_score,
                "consensus_score": consensus_score,
                "confidence_score": confidence_score,
                "agreement_score": agreement_score,
                "completeness_score": completeness_score,
                "learning_style_score": learning_style_score,
                "provider_contributions": provider_contributions,
                "classification": classification,
                "provider_stats": provider_stats,
                "num_successful_providers": len(successful_providers),
                # Phase 3
                "diversity_score": diversity_score,
                "coverage_score": coverage_score,
                "learning_style_verification": learning_style_verification,
                "explanation": explanation,
                "evaluation_summary": evaluation_summary,
                "confidence_level": confidence_level,
                "conflicting_concepts": conflicting_concepts,
                # Phase 4
                "cache_hit": cache_hit,
                "parallel_efficiency": parallel_efficiency,
                "error": None
            }
            
            print(f"Execution time: {execution_time:.2f}s")
            print(f"Cache Hit: {cache_hit}")
            print(f"Parallel Efficiency: {parallel_efficiency:.2f}")
            print(f"Winner: {winning_provider}")
            print(f"Prompt Score: {prompt_score}/100")
            print(f"Consensus Score: {consensus_score:.2f}")
            print(f"Agreement Score: {agreement_score:.2f}")
            print(f"Diversity Score: {diversity_score:.2f}")
            print(f"Coverage Score: {coverage_score:.2f}")
            print(f"Classification: {classification}")
            print(f"Evaluation Summary: {evaluation_summary}")
            print(f"Explanation: {explanation}")
            print(f"Providers Participated: {len(successful_providers)}\n")
            print("--------------------------------------------------")
            print("Providers Attempted:")
            for p in provider_stats:
                model_str = f" ({p.get('model_name', 'unknown')})" if p.get('model_name') != 'unknown' else ""
                if p["success"]:
                    print(f"✓ {p['provider_name']}{model_str}")
                else:
                    msg = p['error_message']
                    reason = ""
                    if "400" in msg and "credit" in msg.lower():
                        reason = "Credit balance too low"
                    elif "402" in msg and "balance" in msg.lower():
                        reason = "Insufficient balance"
                    elif "429" in msg or "rate limit" in msg.lower():
                        reason = "429 Rate limit exceeded"
                    elif "TimeoutError" in msg:
                        reason = "Timeout"
                    else:
                        reason = (msg[:40] + '...') if len(msg) > 40 else msg
                        
                    print(f"✗ {p['provider_name']} ({reason})")
            print("--------------------------------------------------")
                    
            print("\n" + "-" * 32)
            self.results.append(run_result)
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"Execution time: {execution_time:.2f}s")
            print(f"Error occurred: {str(e)}\n")
            traceback.print_exc()
            print("-" * 32)
            
            provider_stats = []
            if hasattr(self.council, "council_executor"):
                failed_providers_list = getattr(self.council.council_executor, "failed_providers", [])
                error_details_dict = getattr(self.council.council_executor, "error_details", {})
                for p_name in failed_providers_list:
                    err_detail = error_details_dict.get(p_name, "Unknown error")
                    if isinstance(err_detail, dict):
                        status_str = err_detail.get("status_code", "N/A")
                        msg = err_detail.get("message", "Unknown")
                        err_type = err_detail.get("type", "Error")
                        error_message = f"{status_str} {err_type}: {msg}" if status_str != "N/A" else f"{err_type}: {msg}"
                    else:
                        error_message = str(err_detail)
                        
                    provider_stats.append({
                        "provider_name": p_name,
                        "model_name": "unknown",
                        "success": False,
                        "latency": 0.0,
                        "response_length": 0,
                        "error_message": error_message
                    })
                    
            run_result = {
                "topic": prompt_data["topic"],
                "learning_style": prompt_data["learning_style"],
                "execution_time": execution_time,
                "winning_provider": "error",
                "contributors": [],
                "prompt_score": 0.0,
                "consensus_score": 0.0,
                "confidence_score": 0.0,
                "agreement_score": 0.0,
                "completeness_score": 0.0,
                "learning_style_score": 0.0,
                "provider_contributions": {},
                "classification": "error",
                "provider_stats": provider_stats,
                "num_successful_providers": 0,
                "diversity_score": 0.0,
                "coverage_score": 0.0,
                "learning_style_verification": {},
                "explanation": "",
                "evaluation_summary": "",
                "confidence_level": "Unknown",
                "conflicting_concepts": [],
                "cache_hit": False,
                "parallel_efficiency": 0.0,
                "error": str(e)
            }
            self.results.append(run_result)
            return run_result

    def compute_statistics(self):
        if not self.results:
            return {}
            
        total_runs = len(self.results)
        successful_runs = [r for r in self.results if r["error"] is None]
        
        num_successful = len(successful_runs)
        if num_successful == 0:
            return {"total_runs": total_runs, "error": "All runs failed"}
            
        avg_exec_time = sum(r["execution_time"] for r in successful_runs) / num_successful
        
        # Phase 4 Stats
        cache_hits = sum(1 for r in successful_runs if r.get("cache_hit"))
        cache_hit_ratio = cache_hits / num_successful if num_successful > 0 else 0.0
        avg_parallel_efficiency = sum(r.get("parallel_efficiency", 1.0) for r in successful_runs) / num_successful
        
        # Get Rankings
        provider_rankings = []
        if hasattr(self.council, "council_executor"):
            provider_rankings = self.council.council_executor.health_tracker.get_provider_rankings()
        
        # Provider specific stats across all runs
        provider_latencies = {}
        provider_attempts = Counter()
        provider_successes = Counter()
        winning_providers = Counter()
        provider_errors = {}
        
        for r in self.results:
            if r["winning_provider"] not in ("none", "error", "timeout"):
                winning_providers[r["winning_provider"]] += 1
                
            for stat in r["provider_stats"]:
                p_name = stat["provider_name"]
                provider_attempts[p_name] += 1
                if stat["success"]:
                    provider_successes[p_name] += 1
                    provider_latencies.setdefault(p_name, []).append(stat["latency"])
                else:
                    if stat["error_message"]:
                        provider_errors.setdefault(p_name, []).append(stat["error_message"])
                    
        # Get list of providers directly from registry and use their display names
        registry = ProviderRegistry()
        self.active_providers = [p.get_provider_name() for p in registry.get_all_providers().values()]
        
        fastest_provider = None
        slowest_provider = None
        avg_provider_latencies = {}
        
        if provider_latencies:
            avg_provider_latencies = {
                p: sum(lats)/len(lats) for p, lats in provider_latencies.items()
            }
            fastest_provider = min(avg_provider_latencies, key=avg_provider_latencies.get)
            slowest_provider = max(avg_provider_latencies, key=avg_provider_latencies.get)
            
        provider_success_rates = {
            p: (provider_successes[p] / provider_attempts[p]) * 100
            for p in provider_attempts if provider_attempts[p] > 0
        }
        
        prompt_scores = [r["prompt_score"] for r in successful_runs]
        
        # New Phase 3 aggregations
        conflicts_all = [c for r in successful_runs for c in r.get("conflicting_concepts", [])]
        most_common_conflict = Counter(conflicts_all).most_common(1)[0][0] if conflicts_all else "None"
        
        ls_verifications = [r.get("learning_style_verification", {}).get("confidence", 0) for r in successful_runs]
        avg_ls_accuracy = sum(ls_verifications) / num_successful if ls_verifications else 0.0

        stats = {
            "total_runs": total_runs,
            "successful_runs": num_successful,
            "avg_execution_time": avg_exec_time,
            "cache_hit_ratio": cache_hit_ratio,
            "avg_parallel_efficiency": avg_parallel_efficiency,
            "provider_rankings": provider_rankings,
            "provider_stats": {"provider_success_rates": provider_success_rates, "provider_errors": provider_errors},
            "fastest_provider": fastest_provider,
            "slowest_provider": slowest_provider,
            "avg_prompt_score": sum(prompt_scores) / num_successful,
            "highest_prompt_score": max(prompt_scores) if prompt_scores else 0,
            "lowest_prompt_score": min(prompt_scores) if prompt_scores else 0,
            "avg_consensus_score": sum(r["consensus_score"] for r in successful_runs) / num_successful,
            "avg_confidence_score": sum(r.get("confidence_score", 0) for r in successful_runs) / num_successful,
            "avg_agreement_score": sum(r.get("agreement_score", 0) for r in successful_runs) / num_successful,
            "avg_diversity_score": sum(r.get("diversity_score", 0) for r in successful_runs) / num_successful,
            "avg_coverage_score": sum(r.get("coverage_score", 0) for r in successful_runs) / num_successful,
            "avg_completeness_score": sum(r.get("completeness_score", 0) for r in successful_runs) / num_successful,
            "avg_learning_style_score": sum(r.get("learning_style_score", 0) for r in successful_runs) / num_successful,
            "avg_learning_style_accuracy": avg_ls_accuracy,
            "most_common_conflict": most_common_conflict,
            "provider_success_rates": provider_success_rates,
            "provider_failure_rates": {p: 100 - r for p, r in provider_success_rates.items()},
            "avg_successful_providers": sum(r["num_successful_providers"] for r in successful_runs) / num_successful,
            "most_frequent_winner": winning_providers.most_common(1)[0][0] if winning_providers else "none",
            "winning_frequencies": dict(winning_providers),
            "avg_provider_latencies": avg_provider_latencies,
            "provider_errors": provider_errors
        }
        return stats
        
    def generate_reports(self, stats):
        if not stats or ("error" in stats and len(stats) == 2):
            print("No valid results to generate reports.")
            return
            
        print("Writing report...")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON Report
        json_path = self.reports_dir / "benchmark_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "statistics": stats,
                "runs": self.results
            }, f, indent=2)
            
        # CSV Report (Summary of runs)
        csv_path = self.reports_dir / "benchmark_results.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Topic", "Learning Style", "Execution Time (s)", 
                "Winning Provider", "Contributors", "Failed Providers", "Prompt Score", 
                "Consensus Score", "Agreement Score", "Diversity Score", "Coverage Score", "Classification", "Error"
            ])
            for r in self.results:
                failed_p = [f"{s['provider_name']}" for s in r.get("provider_stats", []) if not s["success"]]
                
                writer.writerow([
                    r["topic"], r["learning_style"], f"{r['execution_time']:.2f}",
                    r["winning_provider"], ", ".join(r["contributors"]),
                    ", ".join(failed_p),
                    r["prompt_score"], f"{r['consensus_score']:.2f}",
                    f"{r.get('agreement_score', 0):.2f}",
                    f"{r.get('diversity_score', 0):.2f}",
                    f"{r.get('coverage_score', 0):.2f}",
                    r["classification"], r["error"] or ""
                ])
                
        # CSV Report (Provider Attempts)
        csv_provider_path = self.reports_dir / "benchmark_provider_attempts.csv"
        with open(csv_provider_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Topic", "Provider Name", "Model Name", "Success", "Latency (ms)", "Error Message"
            ])
            for r in self.results:
                topic = r["topic"]
                for p in r.get("provider_stats", []):
                    writer.writerow([
                        topic,
                        p.get("provider_name", "unknown"),
                        p.get("model_name", "unknown"),
                        "Yes" if p.get("success") else "No",
                        f"{p.get('latency', 0.0):.2f}",
                        p.get("error_message") or ""
                    ])
                
        # Markdown Report
        md_path = self.reports_dir / "benchmark_summary.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# AI Council Benchmark Report\n\n")
            
            f.write(f"- **Number of benchmark runs:** {stats['total_runs']}\n")
            f.write(f"- **Average prompt score:** {stats['avg_prompt_score']:.2f}\n")
            f.write(f"- **Average consensus score:** {stats['avg_consensus_score']:.2f}\n")
            f.write(f"- **Average confidence score:** {stats['avg_confidence_score']:.2f}\n")
            f.write(f"- **Average agreement score:** {stats['avg_agreement_score']:.2f}\n")
            f.write(f"- **Average diversity score:** {stats.get('avg_diversity_score', 0):.2f}\n")
            f.write(f"- **Average coverage score:** {stats.get('avg_coverage_score', 0):.2f}\n")
            f.write(f"- **Average completeness score:** {stats['avg_completeness_score']:.2f}\n")
            f.write(f"- **Average learning style score:** {stats['avg_learning_style_score']:.2f}\n")
            f.write(f"- **Average learning style accuracy:** {stats.get('avg_learning_style_accuracy', 0):.2f}\n")
            f.write(f"- **Most common conflict:** {stats.get('most_common_conflict', 'None')}\n")
            f.write(f"- **Average successful providers:** {stats['avg_successful_providers']:.2f}\n")
            f.write(f"- **Average execution time:** {stats['avg_execution_time']:.2f}s\n")
            f.write(f"- **Cache hit ratio:** {stats['cache_hit_ratio']*100:.1f}%\n")
            f.write(f"- **Average parallel efficiency:** {stats['avg_parallel_efficiency']*100:.1f}%\n")
            f.write(f"- **Fastest provider:** {stats['fastest_provider']}\n")
            f.write(f"- **Slowest provider:** {stats['slowest_provider']}\n\n")
            
            f.write("## Provider success table\n")
            f.write("| Provider | Success Rate | Avg Latency (ms) | Wins | Common Error |\n")
            f.write("|----------|--------------|------------------|------|--------------|\n")
            
            for provider, rate in stats['provider_success_rates'].items():
                latency = stats['avg_provider_latencies'].get(provider, 0)
                wins = stats['winning_frequencies'].get(provider, 0)
                
                error_str = "-"
                if provider in stats.get("provider_errors", {}):
                    errors = stats["provider_errors"][provider]
                    if errors:
                        common_error = Counter(errors).most_common(1)[0][0]
                        # truncate error string if too long
                        error_str = common_error[:50] + "..." if len(common_error) > 50 else common_error
                        
                f.write(f"| {provider} | {rate:.1f}% | {latency:.1f} | {wins} | {error_str} |\n")
                
            f.write("\n## Winning provider frequency\n")
            for p, w in stats['winning_frequencies'].items():
                f.write(f"- {p}: {w}\n")
                
            f.write("\n## Average provider latency\n")
            for p, l in stats['avg_provider_latencies'].items():
                f.write(f"- {p}: {l:.1f} ms\n")
                
            if stats.get('provider_rankings'):
                f.write("\n## Provider Rankings (Phase 4)\n")
                f.write("| Rank | Provider | Score | Success Rate | Avg Latency |\n")
                f.write("|------|----------|-------|--------------|-------------|\n")
                for i, r in enumerate(stats['provider_rankings'], 1):
                    f.write(f"| {i} | {r['provider_name']} | {r['score']:.1f} | {r['success_rate']*100:.1f}% | {r['average_response_time']:.1f}s |\n")
                
            # Examples
            successful_runs = [r for r in self.results if r["error"] is None]
            if successful_runs:
                successful_runs.sort(key=lambda x: x["prompt_score"], reverse=True)
                high_run = successful_runs[0]
                low_run = successful_runs[-1]
                
                f.write("\n## Example high-quality prompt\n")
                f.write(f"- **Topic:** {high_run['topic']}\n")
                f.write(f"- **Score:** {high_run['prompt_score']}\n")
                f.write(f"- **Winner:** {high_run['winning_provider']}\n")
                
                f.write("\n## Example low-quality prompt\n")
                f.write(f"- **Topic:** {low_run['topic']}\n")
                f.write(f"- **Score:** {low_run['prompt_score']}\n")
                f.write(f"- **Winner:** {low_run['winning_provider']}\n")
                
            f.write("\n## Overall conclusions\n")
            f.write("The AI Council successfully orchestrates multiple models. ")
            f.write(f"The most frequent winner is {stats['most_frequent_winner']}. ")
            f.write("Benchmarking complete.\n")
            
    async def run_all(self):
        prompts = self.load_prompts()
        
        # For debugging purposes, run only the first 3 prompts
        prompts = prompts[:3]
        total = len(prompts)
        
        for i, prompt in enumerate(prompts, 1):
            await self.run_single_benchmark(prompt, i, total)
            
        stats = self.compute_statistics()
        if not stats or "error" in stats and len(stats) == 2:
            print("Benchmarks failed entirely.")
            return
            
        self.generate_reports(stats)
        
        print("\n========== AI Council Benchmark Summary ==========")
        print(f"Average Prompt Score: {stats['avg_prompt_score']:.2f}")
        print(f"Average Consensus Score: {stats['avg_consensus_score']:.2f}")
        print(f"Average Confidence Score: {stats['avg_confidence_score']:.2f}")
        print(f"Average Agreement Score: {stats['avg_agreement_score']:.2f}")
        print(f"Average Diversity Score: {stats.get('avg_diversity_score', 0):.2f}")
        print(f"Average Coverage Score: {stats.get('avg_coverage_score', 0):.2f}")
        print(f"Average Completeness Score: {stats['avg_completeness_score']:.2f}")
        print(f"Average Learning Style Score: {stats['avg_learning_style_score']:.2f}")
        print(f"Average Learning Style Accuracy: {stats.get('avg_learning_style_accuracy', 0):.2f}")
        print(f"Most Common Conflict: {stats.get('most_common_conflict', 'None')}")
        print(f"Average Successful Providers: {stats['avg_successful_providers']:.2f}")
        print(f"Average Execution Time: {stats['avg_execution_time']:.2f}s")
        print(f"Cache Hit Ratio: {stats['cache_hit_ratio']*100:.1f}%")
        print(f"Average Parallel Efficiency: {stats['avg_parallel_efficiency']*100:.1f}%")
        print(f"Fastest Provider: {stats['fastest_provider']}")
        print(f"Slowest Provider: {stats['slowest_provider']}")
        
        if stats.get('provider_rankings'):
            print("\nProvider Rankings:")
            for i, r in enumerate(stats['provider_rankings'], 1):
                print(f"{i}. {r['provider_name']} (Score: {r['score']:.1f})")
        
        print("\nProvider Success Rates:")
        for p, r in stats['provider_success_rates'].items():
            print(f"- {p}: {r:.1f}%")
            
        print("\nWinner Frequency:")
        for p, w in stats['winning_frequencies'].items():
            print(f"- {p}: {w}")
            
        print("\nProvider Contribution Summary:")
        # aggregate contributions
        provider_contrib = {}
        for r in self.results:
            for p, contribs in r.get("provider_contributions", {}).items():
                if p not in provider_contrib:
                    provider_contrib[p] = []
                provider_contrib[p].extend(contribs)
                
        for p, contribs in provider_contrib.items():
            unique_c = list(set(contribs))
            print(f"- {p}: {len(unique_c)} unique concepts/strengths contributed")
            
        print("\nBenchmark completed successfully.")
        print("Reports saved to /reports")


if __name__ == "__main__":
    runner = BenchmarkRunner(
        data_path=str(Path(__file__).resolve().parent.parent / "data" / "benchmark_prompts.json"),
        reports_dir=str(Path(__file__).resolve().parent.parent / "reports")
    )
    asyncio.run(runner.run_all())
