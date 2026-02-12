#!/usr/bin/env python3
"""
Analyze GPX processing metrics for Celery evaluation.

Usage:
    python scripts/analyze_gpx_metrics.py backend.log
"""

import json
import sys
from collections import Counter
from datetime import datetime


def analyze_metrics(log_file):
    """Parse log file and extract GPX metrics."""
    metrics = []

    with open(log_file, 'r') as f:
        for line in f:
            try:
                # Look for structured log entries
                if 'metric_type' in line:
                    # Extract JSON portion (after timestamp and level)
                    json_start = line.find('{')
                    if json_start != -1:
                        data = json.loads(line[json_start:])
                        metrics.append(data)
            except (json.JSONDecodeError, ValueError):
                continue

    return metrics


def generate_report(metrics):
    """Generate analysis report."""
    uploads = [m for m in metrics if m.get('metric_type') == 'gpx_upload']
    completions = [m for m in metrics if m.get('metric_type') == 'gpx_processing_complete']
    errors = [m for m in metrics if m.get('metric_type') == 'gpx_processing_error']

    # File size analysis
    file_sizes = [m['file_size_mb'] for m in uploads if 'file_size_mb' in m]
    large_files = [s for s in file_sizes if s > 5]

    # Processing time analysis
    proc_times = [m['processing_time_seconds'] for m in completions if 'processing_time_seconds' in m]
    slow_processing = [t for t in proc_times if t > 30]

    # Processing mode distribution
    modes = Counter([m.get('processing_mode') for m in completions])

    print("=" * 60)
    print("GPX METRICS ANALYSIS REPORT")
    print("=" * 60)
    print()

    print(f"📊 UPLOAD STATISTICS")
    print(f"   Total uploads: {len(uploads)}")
    if file_sizes:
        print(f"   Average file size: {sum(file_sizes) / len(file_sizes):.2f} MB")
        print(f"   Max file size: {max(file_sizes):.2f} MB")
        print(f"   Min file size: {min(file_sizes):.2f} MB")
    print()

    print(f"📈 PROCESSING STATISTICS")
    print(f"   Successful: {len(completions)}")
    print(f"   Failed: {len(errors)}")
    if completions:
        success_rate = len(completions) / (len(completions) + len(errors)) * 100
        print(f"   Success rate: {success_rate:.1f}%")
    print()

    if proc_times:
        print(f"⏱️  PROCESSING TIME")
        print(f"   Average: {sum(proc_times) / len(proc_times):.2f}s")
        print(f"   Max: {max(proc_times):.2f}s")
        print(f"   Min: {min(proc_times):.2f}s")
        print(f"   >30s (slow): {len(slow_processing)} ({len(slow_processing) / len(proc_times) * 100:.1f}%)")
    print()

    print(f"🔄 PROCESSING MODE")
    for mode, count in modes.items():
        print(f"   {mode}: {count} ({count / len(completions) * 100:.1f}%)")
    print()

    print("=" * 60)
    print("🎯 CELERY ADOPTION DECISION CRITERIA")
    print("=" * 60)
    print()

    # Criterion 1: Files >5MB
    large_file_pct = (len(large_files) / len(file_sizes) * 100) if file_sizes else 0
    criterion1 = large_file_pct > 20
    status1 = "✅ PASS" if criterion1 else "❌ FAIL"
    print(f"1. Files >5MB: {len(large_files)}/{len(file_sizes)} ({large_file_pct:.1f}%) {status1}")
    print(f"   Threshold: >20% → {'IMPLEMENT CELERY' if criterion1 else 'BackgroundTasks OK'}")
    print()

    # Criterion 2: Slow processing
    slow_pct = (len(slow_processing) / len(proc_times) * 100) if proc_times else 0
    criterion2 = slow_pct > 10
    status2 = "✅ PASS" if criterion2 else "❌ FAIL"
    print(f"2. Processing >30s: {len(slow_processing)}/{len(proc_times)} ({slow_pct:.1f}%) {status2}")
    print(f"   Threshold: >10% → {'IMPLEMENT CELERY' if criterion2 else 'BackgroundTasks OK'}")
    print()

    # Criterion 3: Error rate
    error_rate = (len(errors) / (len(completions) + len(errors)) * 100) if (completions or errors) else 0
    criterion3 = error_rate > 5
    status3 = "✅ PASS" if criterion3 else "❌ FAIL"
    print(f"3. Error rate: {error_rate:.1f}% {status3}")
    print(f"   Threshold: >5% → {'INVESTIGATE' if criterion3 else 'Normal'}")
    print()

    # Final recommendation
    criteria_passed = sum([criterion1, criterion2])
    print("=" * 60)
    if criteria_passed >= 2:
        print("🚀 RECOMMENDATION: IMPLEMENT CELERY + REDIS")
        print("   Rationale: ≥2 criteria met, BackgroundTasks insufficient")
    elif criteria_passed == 1:
        print("⚠️  RECOMMENDATION: MONITOR FOR ANOTHER MONTH")
        print("   Rationale: 1 criterion met, borderline case")
    else:
        print("✅ RECOMMENDATION: KEEP BACKGROUNDTASKS")
        print("   Rationale: Current solution adequate, no action needed")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_gpx_metrics.py <log_file>")
        sys.exit(1)

    log_file = sys.argv[1]
    metrics = analyze_metrics(log_file)

    if not metrics:
        print(f"⚠️  No metrics found in {log_file}")
        sys.exit(1)

    generate_report(metrics)
