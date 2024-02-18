sudo nerdctl run --name aixp_ee_container --rm --network=host -v /var/cache/aixp_ee/_local_cache:/exe_eng/_local_cache -e EE_ID=stg_k8s_super aixpand/exe_eng:develop
