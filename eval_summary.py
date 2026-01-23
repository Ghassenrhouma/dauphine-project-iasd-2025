import pandas as pd

df = pd.read_excel('evaluation_results.xlsx')

perfect = df[df['Score'] == 5]
good = df[(df['Score'] >= 3) & (df['Score'] < 5)]
poor = df[df['Score'] <= 2]

print("=" * 80)
print("EVALUATION SUMMARY")
print("=" * 80)
print(f"\nScore Distribution:")
print(f"  Perfect (5/5):     {len(perfect)}/25 ({len(perfect)/25*100:.1f}%)")
print(f"  Good (3-4/5):      {len(good)}/25 ({len(good)/25*100:.1f}%)")
print(f"  Needs Work (0-2):  {len(poor)}/25 ({len(poor)/25*100:.1f}%)")

print(f"\n\nPERFECT SCORES (5/5) - {len(perfect)} questions:")
for _, row in perfect.iterrows():
    print(f"  ✓ [{row['Difficulty']:14}] {row['Question'][:60]}...")

print(f"\n\nNEEDS IMPROVEMENT (≤2/5) - {len(poor)} questions:")
for _, row in poor.iterrows():
    print(f"  ✗ [{row['Score']}/5 - {row['Difficulty']:14}] {row['Question'][:50]}...")
