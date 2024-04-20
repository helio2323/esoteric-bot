import asyncio
import sys
import os

# Adiciona o diretório atual ao caminho de pesquisa do Python
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from bot import check_profiles

async def main():
    await check_profiles('1713480487576x673188887945805800')

if __name__ == "__main__":
    asyncio.run(main())
