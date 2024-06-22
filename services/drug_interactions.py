import asyncio
from typing import List, Dict, Any

from models import DDIModel
from storage import Storage


async def interaction_checker_service(drugs: List[str]) -> List[Dict[str, Any]]:
    # Create a list to store the tasks for each drug pair
    tasks = [
        Storage.filter(DDIModel, {DDIModel.drug_ref_1: drugs[i], DDIModel.drug_ref_2: drugs[j]})
        for i in range(len(drugs))
        for j in range(i + 1, len(drugs))
    ]

    # Run the tasks concurrently
    interactions = await asyncio.gather(*tasks)
    results = []
    index = 0
    for i in range(len(drugs)):
        for j in range(i + 1, len(drugs)):
            interaction = interactions[index]
            index += 1
            if interaction:
                results.append({
                    "drug_ref_1": interaction[0].drug_ref_1,
                    "drug_ref_2": interaction[0].drug_ref_2,
                    "interaction": interaction[0].interaction
                })
            else:
                results.append({
                    "drug_ref_1": drugs[i],
                    "drug_ref_2": drugs[j],
                    "interaction": -1
                })

    return results
