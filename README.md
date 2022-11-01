This repository contains artifacts for the paper:

**Light, Camera, Actions: characterizing the usage of IXPs' action BGP communities**<br>
*Fabricio Mazzola (fmmazzola@inf.ufrgs.br), Pedro Marcos (pbmarcos@furg.br) and Marinho Barcellos (marinho.barcellos@waikato.ac.nz)*<br>

The artefacts in this repository can be used to reproduce the main results of the paper or to extend our work.


The BGP files located in *BGPFiles/* **do not** need to be unzipped when using the *processRSCommunityData.py* script.<br>


When using any of the scripts to reproduce our results, please, first **unzip all the files** located at *preprocessed_bgp_communities_data/* <br>


The repository itself is structured as follows:

~~~
.
|
├── processRSCommunityData.py                   # Script to process BGP Files for an IXP and output pre-processed information about BGP Communities seen at it.
|                                               # Its outputs are located at preprocessed_bgp_communities_data/
|
├── BGPFiles/                                   # BGP Files used to generate the paper's results
│   ├── ixbr/
│   ├── amsix/
│   ├── linx/
│   ├── decix/ (contains files for DE-CIX Frankfurt)
│   ├── bcix/
│   ├── decixothers/ (contains files for DE-CIX MAD and DE-CIX NYC)
│   └── netnod/
|
├── pre_process_action_communities_data.py       # Scripts to generate a pre-processed JSON with the action BGP Communities used at each IXP
|
|
├── preprocessed_bgp_communities_data/           # Files obtained by the usage of processRSCommunityData.py and pre_process_action_communities_data.py
|
|
└── process_ixpCommvsNonIxpComm/                 # Reproduce results of Figure 1
|   ├── process_ixpCommvsNonIxpComm.py
|   └── output_data
|
├── process_communityPerType/                    # Reproduce results of Figure 2
│   ├── output_data
│   └── process_communityPerType.py
| 
├── process_actionVsInfo/                        # Reproduce results of Figure 3
│   ├── output_data
│   └── process_actionVsInfo.py
|
├── process_asesUsingActionCommBar/              # Reproduce results of Figure 4a
│   ├── process_asesUsingActionCommBar.py
│   └── output_data
|
├── process_asesApplyingMoreActionCommunities/   # Reproduce results of Figure 4b
│   ├── output_data
│   └── process_asesApplyingMoreActionCommunities.py
|
├── process_scatterPrefixesvsCommunities/        # Reproduce results of Figure 4c
│   ├── output_data
│   └── process_scatterPrefixesvsCommunities.py
|
├── process_communitiesMostUsed/                 # Reproduce results of Figure 5
│   ├── output_data
│   └── process_communitiesMostUsed.py
|
├── process_asesNotMembersMoreTargetted/         # Reproduce results of Figure 6
│   ├── process_asesNotMembersMoreTargetted.py
│   └── output_data
|
├── process_asesApplyingCommToNonRSASes/         # Reproduce results of Figure 7
│   ├── output_data
│   └── process_asesApplyingCommToNonRSASes.py
|
|
├── process_asesUsingEachActionCommunityCategory/  # Reproduce results of Table 2
│   ├── output_data
│   └── process_asesUsingEachActionCommunityCategory.py
|
|
|
├── tools/                                      # Files containing the used BGP communities dictionaries, ASes with UP sessions at the RSs,
│   ├── communitiesDictionaries/                # information about AS Type obtained via PeeringDB and help functions used across the multiple
│   ├── asesInRS.txt                            # scripts to reproduce results
│   ├── asnInfo.txt
│   ├── __init__.py
│   ├── help_functions.py
│   └── constants.py
|   |
|   ├── build_dictionaries/                          # Scripts to obtain the BGP Communities dictionaries from IXP Route Servers
│       |
|       └── buildCommunitiesDictAuto.py
|
|
├──

~~~


We relied on the following versions for our Python 3.8.9 imports (all of which can be installed via pip3) using the requirements.py file: 

~~~
cycler==0.11.0
matplotlib==3.5.2
numpy==1.23.1
pandas==1.4.2
plotly==5.8.0
pyparsing==3.0.9
tabulate==0.8.9
tqdm==4.64.0
~~~
